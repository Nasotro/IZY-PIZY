"""Story visuals: one image, or a short animation built from word icons.

Flow for ``kind="video"``:

1. Mistral (the "director") decides which objects open the scene, which ones
   appear during the clip, and writes the three prompts (start / end / motion).
2. Both keyframes are generated with FLUX.2, feeding the word icons of the
   relevant objects as reference images so the objects keep their identity.
3. FLUX.3 animates between the two keyframes (draft by default: it is free).

Everything stays synchronous; nginx is configured with a 900s read timeout and
a 5s draft clip takes ~60-90s end to end.
"""

from __future__ import annotations

import uuid

from aiosqlite import Connection
from fastapi import APIRouter, Depends, HTTPException

import config
from database import get_db
from dependencies import CurrentUser, get_current_user
from models.blackforest_image_generation import MODEL_TIERS, generate_image_from_prompt
from models.blackforest_video import file_to_data_url, generate_video_from_keyframes
from models.stories import VisualOptions, VisualResult
from models.visual_director import plan_animation, plan_still_scene

router = APIRouter()

MAX_REFERENCES = {"small": 4, "big": 8}
DRAFT_COST_HINT = {"5": "~$0.75", "8": "~$1.20", "10": "~$1.50", "12": "~$1.80"}


def _aspect_ratio(width: int, height: int) -> str:
    if width == height:
        return "1:1"
    return "16:9" if width > height else "9:16"


def _reference_legend(entries: list[str]) -> str:
    """Tell FLUX what each reference image contains, in order."""
    if not entries:
        return ""
    pairs = "; ".join(f"image {i + 1} = {entry}" for i, entry in enumerate(entries))
    return f" Reference images: {pairs}. Reuse those objects unchanged in shape and colour."


async def _load_story(db: Connection, user_id: str, story_id: int):
    async with db.execute(
        "SELECT * FROM stories WHERE id = ? AND user_id = ?", (story_id, user_id)
    ) as cursor:
        row = await cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Story not found")
    return row


async def _icon_paths(db: Connection, user_id: str, words: list[str]) -> dict[str, str]:
    """word_key -> stored image path, for the words that have an icon."""
    if not words:
        return {}
    keys = sorted({w.strip().lower() for w in words if w.strip()})
    placeholders = ",".join("?" for _ in keys)
    async with db.execute(
        f"SELECT word_key, image_path FROM word_icons WHERE user_id = ? AND word_key IN ({placeholders})",
        (user_id, *keys),
    ) as cursor:
        rows = await cursor.fetchall()
    return {row["word_key"]: row["image_path"] for row in rows}


def _build_refs(words: list[str], icons: dict[str, str]) -> list[str]:
    refs = []
    for word in words:
        path = icons.get(word.strip().lower())
        if path:
            absolute = config.IMAGE_STORAGE_DIR / path
            if absolute.exists():
                refs.append(file_to_data_url(absolute))
    return refs[:8]


@router.post("/stories/{story_id}/generate-visual", response_model=VisualResult)
async def generate_story_visual(
    story_id: int,
    body: VisualOptions | None = None,
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    body = body or VisualOptions()
    user_id = current_user.uid
    notes: list[str] = []

    kind = (body.kind or "image").strip().lower()
    if kind not in {"image", "video"}:
        raise HTTPException(status_code=400, detail="kind must be 'image' or 'video'")

    row = await _load_story(db, user_id, story_id)
    sentence = (row["sentence"] or "").strip()
    words = [row[f"word_{i}"] for i in range(5)]
    words = [w.strip() for w in words if w and w.strip()]
    if not sentence:
        raise HTTPException(status_code=400, detail="Story has no sentence to generate a visual from")

    model = (body.model or "big").strip().lower()
    if model not in MODEL_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model tier '{model}'. Valid values: {', '.join(MODEL_TIERS)}",
        )

    # ---- word icons -------------------------------------------------------
    icons: dict[str, str] = {}
    if body.use_word_icons:
        icons = await _icon_paths(db, user_id, words)
        missing = [w for w in words if w.strip().lower() not in icons]
        if missing:
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Some words have no icon yet, so this sentence cannot use word icons.",
                    "missing_words": missing,
                },
            )
        if model == "small" and len(words) > MAX_REFERENCES["small"]:
            notes.append(
                f"'small' accepts {MAX_REFERENCES['small']} reference images; switched to 'big' for {len(words)} icons."
            )
            model = "big"

    if not config.BFL_API_KEY and not config.LOCAL_MODE:
        raise HTTPException(status_code=500, detail="Blackforest API key not configured")

    image_dir = config.IMAGE_STORAGE_DIR
    image_dir.mkdir(parents=True, exist_ok=True)

    # ---- images -----------------------------------------------------------
    if kind == "image":
        plan = None
        if body.custom_prompt and body.custom_prompt.strip():
            base_prompt = body.custom_prompt.strip()
        elif body.use_mistral_enhancement:
            plan = await plan_still_scene(sentence, words)
            base_prompt = plan.get("image_prompt") or plan["start_prompt"]
            if plan.get("rationale"):
                notes.append(f"director: {plan['rationale']}")
        else:
            base_prompt = sentence
            notes.append("no Mistral planning: raw sentence used as prompt")

        refs = _build_refs(words, icons) if body.use_word_icons else []
        prompt = base_prompt + _reference_legend(words if refs else [])

        num_images = min(max(int(body.num_images or 1), 1), 4)
        generated = []
        for _ in range(num_images):
            filename = f"story_{story_id}_{uuid.uuid4().hex}.png"
            absolute = image_dir / filename
            try:
                await generate_image_from_prompt(
                    prompt,
                    str(absolute),
                    width=body.width,
                    height=body.height,
                    model=model,
                    timeout=float(body.timeout),
                    auto_rephrase=body.auto_rephrase,
                    reference_images=refs or None,
                    output_format="png",
                )
            except Exception as exc:
                raise HTTPException(status_code=502, detail=f"Image generation failed: {exc}")
            generated.append(
                {"path": filename, "url": f"{config.IMAGE_BASE_URL}/{filename}"}
            )

        first = generated[0]["path"]
        await db.execute(
            "UPDATE stories SET image_path = ?, visual_kind = 'image' WHERE id = ? AND user_id = ?",
            (first, story_id, user_id),
        )
        await db.commit()
        row = await _load_story(db, user_id, story_id)

        from routers.stories import _row_to_story

        return VisualResult(
            story=_row_to_story(row),
            kind="image",
            images=generated,
            plan=plan,
            notes=notes,
        )

    # ---- video ------------------------------------------------------------
    if config.LOCAL_MODE:
        raise HTTPException(
            status_code=400,
            detail="Video generation needs a Blackforest API key; it is unavailable in local mode.",
        )

    duration = min(max(int(body.duration or 5), 5), 20)
    if body.use_mistral_enhancement:
        plan = await plan_animation(sentence, words, duration)
        notes.append(f"director: {plan.get('rationale') or 'plan generated'}")
    else:
        from models.visual_director import _fallback_plan

        plan = _fallback_plan(sentence, words)
        notes.append("Mistral planning disabled: deterministic two-stage plan used")

    start_words = plan.get("start_objects") or words[:2]
    start_words = [w for w in start_words if w.strip().lower() in icons] or (words if body.use_word_icons else [])

    start_refs = _build_refs(start_words, icons) if body.use_word_icons else []

    start_prompt = plan["start_prompt"] + _reference_legend(start_words if start_refs else [])

    start_name = f"story_{story_id}_{uuid.uuid4().hex}_start.png"
    end_name = f"story_{story_id}_{uuid.uuid4().hex}_end.png"
    start_path = image_dir / start_name
    end_path = image_dir / end_name

    try:
        await generate_image_from_prompt(
            start_prompt,
            str(start_path),
            width=body.width,
            height=body.height,
            model=model,
            timeout=float(body.timeout),
            auto_rephrase=body.auto_rephrase,
            reference_images=start_refs or None,
            output_format="png",
        )
        # The end frame is a continuation of the start frame, not a second
        # independent generation: feeding the start frame as the first
        # reference keeps the palette, the camera and the layout identical,
        # which is what makes the interpolation look like one continuous shot.
        end_prompt = (
            "Same scene as the reference image: keep the background, framing, "
            "lighting and illustration style strictly identical. " + plan["end_prompt"]
        )
        # Only the start frame is sent as a reference here: feeding the word
        # icons again made FLUX "rebuild" the scene around a single icon and
        # lose the set (measured: a lone roof tile replaced the whole house).
        end_prompt += _reference_legend(["the opening frame (keep it unchanged)"])
        await generate_image_from_prompt(
            end_prompt,
            str(end_path),
            width=body.width,
            height=body.height,
            model=model,
            timeout=float(body.timeout),
            auto_rephrase=body.auto_rephrase,
            reference_images=[file_to_data_url(start_path)],
            output_format="png",
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Keyframe generation failed: {exc}")

    video_prompt = plan.get("motion_prompt") or (
        "Smooth continuous camera move; the remaining elements enter and settle, no cut, seamless loop."
    )

    video_name = f"story_{story_id}_{uuid.uuid4().hex}.mp4"
    video_path = image_dir / video_name
    try:
        info = await generate_video_from_keyframes(
            video_prompt,
            [(0.0, file_to_data_url(start_path)), (float(duration), file_to_data_url(end_path))],
            str(video_path),
            duration=duration,
            resolution=body.resolution or "hd",
            aspect_ratio=_aspect_ratio(body.width, body.height),
            draft=bool(body.draft),
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Video generation failed: {exc}")

    if body.draft:
        notes.append(f"draft render ({info['elapsed']}s): preview quality, not billed")
    else:
        notes.append(
            f"full render ({info['elapsed']}s): billed ~{DRAFT_COST_HINT.get(str(duration), '?')}"
        )

    await db.execute(
        """
        UPDATE stories
           SET image_path = ?, video_path = ?, start_frame_path = ?, end_frame_path = ?,
               visual_kind = 'video'
         WHERE id = ? AND user_id = ?
        """,
        (start_name, video_name, start_name, end_name, story_id, user_id),
    )
    await db.commit()
    row = await _load_story(db, user_id, story_id)

    from routers.stories import _row_to_story

    story_out = _row_to_story(row)
    return VisualResult(
        story=story_out,
        kind="video",
        images=[{"path": start_name, "url": f"{config.IMAGE_BASE_URL}/{start_name}"},
                {"path": end_name, "url": f"{config.IMAGE_BASE_URL}/{end_name}"}],
        video_url=story_out.video_url,
        start_frame_url=story_out.start_frame_url,
        end_frame_url=story_out.end_frame_url,
        plan=plan,
        notes=notes,
    )
