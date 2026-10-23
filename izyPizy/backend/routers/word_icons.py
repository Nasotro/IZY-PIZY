"""Word icons: one reusable picture per dictionary word.

Icons are keyed by ``word_key`` (lower-cased spelling) rather than by dictionary
row, because the same word legitimately appears under several two-digit numbers
— the learner should draw "chat" once and get it everywhere.

The generated image is a single object on a plain white background so it can be
fed back to FLUX.2 as a reference image when composing a scene.
"""

from __future__ import annotations

import uuid
from pathlib import Path

from aiosqlite import Connection
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import config
from database import get_db
from dependencies import CurrentUser, get_current_user
from models.blackforest_image_generation import MODEL_TIERS, generate_image_from_prompt
from models.visual_director import enhance_icon_prompt

router = APIRouter()

ICON_SIZE = 1024
ICON_DIR = "icons"


class IconRequest(BaseModel):
    description: str | None = None
    model: str = "small"


class IconOut(BaseModel):
    word_id: int
    word: str
    word_key: str
    has_icon: bool
    image_path: str | None = None
    icon_url: str | None = None
    prompt: str | None = None
    user_description: str | None = None
    model: str | None = None
    updated_at: str | None = None


def _icon_storage() -> Path:
    directory = config.IMAGE_STORAGE_DIR / ICON_DIR
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _icon_url(image_path: str | None) -> str | None:
    if not image_path:
        return None
    return f"{config.IMAGE_BASE_URL}/{image_path}"


async def _get_word(db: Connection, user_id: str, word_id: int):
    async with db.execute(
        "SELECT id, word FROM dictionary_words WHERE id = ? AND user_id = ?",
        (word_id, user_id),
    ) as cursor:
        row = await cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Word not found")
    return row


@router.get("/dictionary/words/{word_id}/icon", response_model=IconOut)
async def get_word_icon(
    word_id: int,
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_id = current_user.uid
    word_row = await _get_word(db, user_id, word_id)
    word_key = word_row["word"].strip().lower()

    async with db.execute(
        "SELECT * FROM word_icons WHERE user_id = ? AND word_key = ?",
        (user_id, word_key),
    ) as cursor:
        icon = await cursor.fetchone()

    if icon is None:
        return IconOut(word_id=word_id, word=word_row["word"], word_key=word_key, has_icon=False)

    return IconOut(
        word_id=word_id,
        word=word_row["word"],
        word_key=word_key,
        has_icon=True,
        image_path=icon["image_path"],
        icon_url=_icon_url(icon["image_path"]),
        prompt=icon["prompt"],
        user_description=icon["user_description"],
        model=icon["model"],
        updated_at=icon["updated_at"],
    )


@router.post("/dictionary/words/{word_id}/icon", response_model=IconOut)
async def create_word_icon(
    word_id: int,
    body: IconRequest | None = None,
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Generate (or regenerate) the icon for a word.

    One icon per distinct spelling: generating "chat" from one number also
    fills the icon everywhere else "chat" is used.
    """
    user_id = current_user.uid
    body = body or IconRequest()
    model = (body.model or "small").strip().lower()
    if model not in MODEL_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown model tier '{model}'. Valid values: {', '.join(MODEL_TIERS)}",
        )
    if not config.BFL_API_KEY and not config.LOCAL_MODE:
        raise HTTPException(status_code=500, detail="Blackforest API key not configured")

    word_row = await _get_word(db, user_id, word_id)
    word = word_row["word"]
    word_key = word.strip().lower()
    description = (body.description or "").strip()

    prompt = await enhance_icon_prompt(word, description)

    icon_dir = _icon_storage()
    filename = f"{uuid.uuid4().hex}.png"
    absolute_path = icon_dir / filename
    relative_path = f"{ICON_DIR}/{filename}"

    try:
        await generate_image_from_prompt(
            prompt,
            str(absolute_path),
            width=ICON_SIZE,
            height=ICON_SIZE,
            model=model,
            output_format="png",
            key_elements=[word],
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Icon generation failed: {exc}")

    async with db.execute(
        "SELECT image_path FROM word_icons WHERE user_id = ? AND word_key = ?",
        (user_id, word_key),
    ) as cursor:
        previous = await cursor.fetchone()

    await db.execute(
        """
        INSERT INTO word_icons (user_id, word_key, image_path, user_description, prompt, model, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        ON CONFLICT(user_id, word_key) DO UPDATE SET
            image_path = excluded.image_path,
            user_description = excluded.user_description,
            prompt = excluded.prompt,
            model = excluded.model,
            updated_at = datetime('now')
        """,
        (user_id, word_key, relative_path, description or None, prompt, model),
    )
    await db.commit()

    if previous is not None:
        old_path = previous["image_path"]
        if old_path and old_path != relative_path:
            try:
                (config.IMAGE_STORAGE_DIR / old_path).unlink(missing_ok=True)
            except OSError:
                pass

    return IconOut(
        word_id=word_id,
        word=word,
        word_key=word_key,
        has_icon=True,
        image_path=relative_path,
        icon_url=_icon_url(relative_path),
        prompt=prompt,
        user_description=description or None,
        model=model,
        updated_at=None,
    )


@router.delete("/dictionary/words/{word_id}/icon")
async def delete_word_icon(
    word_id: int,
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_id = current_user.uid
    word_row = await _get_word(db, user_id, word_id)
    word_key = word_row["word"].strip().lower()

    async with db.execute(
        "SELECT image_path FROM word_icons WHERE user_id = ? AND word_key = ?",
        (user_id, word_key),
    ) as cursor:
        icon = await cursor.fetchone()

    if icon is None:
        raise HTTPException(status_code=404, detail="No icon for this word")

    await db.execute(
        "DELETE FROM word_icons WHERE user_id = ? AND word_key = ?", (user_id, word_key)
    )
    await db.commit()

    try:
        (config.IMAGE_STORAGE_DIR / icon["image_path"]).unlink(missing_ok=True)
    except OSError:
        pass

    return {"ok": True}
