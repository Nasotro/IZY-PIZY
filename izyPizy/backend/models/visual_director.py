"""Mistral-side intelligence for word icons and scene storyboarding.

Three entry points:

- ``enhance_icon_prompt``   : one word -> one single-object icon prompt
- ``plan_still_scene``      : sentence + objects -> one hero image prompt
- ``plan_animation``        : sentence + objects -> start/end frames + motion

Each function degrades to a deterministic local template when Mistral is not
configured or returns something unusable, so the app never hard-fails on the
LLM. The fallbacks are deliberately plain but consistent with the same style,
so generated visuals keep looking like the rest of the book.
"""

from __future__ import annotations

import json
import re

import httpx

import config

MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

# Shared visual language. Word icons and scene frames must feel like they come
# from the same illustrator, otherwise pasted references look like stickers.
STYLE = (
    "consistent illustration style: warm digital gouache, soft shading, clean "
    "shapes, gentle cinematic light, no text, no lettering, no watermark, no "
    "frame or border"
)

ICON_STYLE = (
    "flat editorial illustration, soft shading, subtle contact shadow, clean "
    "shapes, single object, no text, no lettering, no watermark, no hands, no "
    "frame, no border"
)


async def _chat(
    messages: list[dict],
    model: str,
    *,
    temperature: float = 0.3,
    max_tokens: int = 700,
    json_mode: bool = False,
    timeout: float = 60.0,
) -> str | None:
    """Call Mistral and return the raw message content (None on any failure)."""
    key = config.MISTRAL_API_KEY
    if not key:
        return None

    payload: dict = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.post(
                MISTRAL_URL,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if r.status_code != 200:
            print(f"[mistral] {model} HTTP {r.status_code}: {r.text[:200]}")
            return None
        return r.json()["choices"][0]["message"]["content"]
    except Exception as exc:  # network, timeout, malformed body...
        print(f"[mistral] {model} error: {exc}")
        return None


def _clean(text: str | None) -> str:
    if not text:
        return ""
    return text.strip().strip('"').strip("\u201c\u201d").strip()


# --------------------------------------------------------------------------
# Word icons
# --------------------------------------------------------------------------

def icon_fallback_prompt(word: str, description: str = "") -> str:
    extra = f" {description.strip().rstrip('.')}." if description.strip() else ""
    return (
        f"A single {word}, shown alone and centred, entire object visible with "
        f"generous margin on a pure white background, soft studio lighting, "
        f"{ICON_STYLE}.{extra}"
    )


async def enhance_icon_prompt(word: str, description: str = "") -> str:
    """Turn a dictionary word into a prompt for one clean, reusable icon."""
    system = f"""You write image-generation prompts for vocabulary flashcards.
Output ONE prompt, in English, 40-80 words, describing a single object as a clean icon.

Hard rules:
- exactly ONE object, seen from a clear readable angle, entire object visible
- pure white background (#FFFFFF), generous empty margin around the object
- soft even studio lighting, subtle contact shadow, no scene, no landscape
- the object stands alone, without a surrounding scene, props or decoration
  (no plate under food, no landscape behind a building)
- pick the most common everyday concrete meaning of the word; these are French
  vocabulary cards, so "tuiles" means clay roof tiles (not almond biscuits) and
  "avocat" means the fruit before the lawyer
- keep the object at its own scale: a roof is the whole tiled structure seen in
  three-quarter view, not a single tile; a single tile is "une tuile"
- if the word is an adjective, a colour, a texture, a feeling or an abstract noun,
  depict it as one concrete visual (e.g. "roux" -> a close-up swatch of ginger fur
  or ginger hair, "joyeux" -> a smiling sun-like face)
- never render letters, words, numbers, captions, logos or watermarks
- style: {ICON_STYLE}

Return only the prompt, no preamble, no quotes."""

    user = f'Word: "{word}"'
    if description.strip():
        user += f'\nThe learner described it as: "{description.strip()}"'
    user += "\nPrompts are consumed by FLUX.2 together with up to 4 reference icons, " \
            "so keep the object description precise and neutral."

    out = _clean(await _chat(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        config.MISTRAL_PROMPT_MODEL,
        temperature=0.4,
        max_tokens=220,
    ))
    if len(out) < 20:
        return icon_fallback_prompt(word, description)
    return out


# --------------------------------------------------------------------------
# Scene planning
# --------------------------------------------------------------------------

def _normalise_plan(raw: dict, objects: list[str]) -> dict | None:
    """Validate/sanitise the director JSON. Returns None if unusable."""
    if not isinstance(raw, dict):
        return None
    start_prompt = _clean(raw.get("start_prompt"))
    end_prompt = _clean(raw.get("end_prompt"))
    motion = _clean(raw.get("motion_prompt"))
    image_prompt = _clean(raw.get("image_prompt"))
    if not (start_prompt or image_prompt):
        return None

    def _pick(value, pool):
        if not isinstance(value, list):
            return []
        wanted = {str(v).strip().lower() for v in value}
        return [o for o in pool if o.strip().lower() in wanted]

    start_objects = _pick(raw.get("start_objects"), objects)
    appearing = _pick(raw.get("appearing_objects"), objects)
    # Any object the model dropped goes to the "appearing" side rather than
    # disappearing from the animation altogether.
    claimed = {o.lower() for o in start_objects + appearing}
    appearing += [o for o in objects if o.lower() not in claimed]
    # Overlap: keep it in the start side only.
    appearing = [o for o in appearing if o.lower() not in {s.lower() for s in start_objects}]

    if not start_objects and objects:
        start_objects = objects[:2]

    return {
        "start_objects": start_objects,
        "appearing_objects": appearing,
        "start_prompt": start_prompt or image_prompt,
        "end_prompt": end_prompt or start_prompt or image_prompt,
        "motion_prompt": motion,
        "image_prompt": image_prompt,
        "rationale": _clean(raw.get("rationale")),
    }


def _fallback_plan(sentence: str, objects: list[str]) -> dict:
    """Deterministic plan used when Mistral is unavailable.

    Split the five objects in two: the first three anchor the opening frame,
    the last two appear during the clip. Not clever, but always coherent and
    it keeps the "objects arrive progressively" behaviour.
    """
    start = objects[:3]
    appearing = objects[3:]
    joined = ", ".join(objects) if objects else sentence
    start_txt = ", ".join(start) if start else joined
    return {
        "start_objects": start,
        "appearing_objects": appearing,
        "start_prompt": (
            f"{sentence}. Opening frame: {start_txt} clearly visible and well "
            f"composed. {STYLE}."
        ),
        "end_prompt": (
            f"{sentence}. Final frame: {joined} all visible together. {STYLE}."
        ),
        "motion_prompt": (
            "Slow gentle camera push-in; the remaining elements enter the scene "
            "and settle into place, no cut, seamless loop."
        ),
        "image_prompt": f"{sentence}. All five objects visible: {joined}. {STYLE}.",
        "rationale": "fallback: first three objects anchor the frame",
    }


DIRECTOR_SYSTEM = f"""You are the storyboard director of a vocabulary flashcard app.
Each card shows one short French sentence and exactly five key objects — the words
the learner has to memorise. Design the visuals that make those five objects
unforgettable.

For a STILL image: compose one rich illustration where all five objects are
clearly readable, no object hidden behind another, natural scene, same style
everywhere.

For an ANIMATION (5 to 8 seconds, seamless loop): choose 2 or 3 objects that are
physically stable in the scene (ground, building, sky, landmark, surface) and put
them in the opening frame — the first frame must already look like a finished
illustration, never an empty stage. The remaining objects APPEAR during the clip
(entering frame, lighting up, growing, sliding in, being revealed). The last frame
contains all of them. One continuous camera, no cuts, no text.

Rules:
- Prompts in English, one paragraph each, max 90 words.
- start_prompt / end_prompt describe still frames; motion_prompt describes only
  the movement between them.
- Keep character and object appearance stable between the two frames.
- Style for every frame: {STYLE}.
- If a word is an adjective or abstract (colour, mood, texture), fold it into the
  object it qualifies instead of inventing a sixth object.

Return ONLY valid JSON:
{{"start_objects": [...], "appearing_objects": [...], "start_prompt": "...",
  "end_prompt": "...", "motion_prompt": "...", "image_prompt": "...",
  "rationale": "max 25 words"}}
For a still image, fill image_prompt and repeat it in start_prompt."""


async def _direct(sentence: str, objects: list[str], duration: int, mode: str) -> dict:
    user = (
        f'Sentence: "{sentence}"\n'
        f'Key objects (in sentence order): {json.dumps(objects, ensure_ascii=False)}\n'
        f"Target: {'a single still image' if mode == 'image' else f'a {duration}-second looping animation'}"
    )
    raw = await _chat(
        [
            {"role": "system", "content": DIRECTOR_SYSTEM},
            {"role": "user", "content": user},
        ],
        config.MISTRAL_DIRECTOR_MODEL,
        temperature=0.4,
        max_tokens=800,
        json_mode=True,
        timeout=90.0,
    )
    if not raw:
        return _fallback_plan(sentence, objects)
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.S)
        if not match:
            return _fallback_plan(sentence, objects)
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return _fallback_plan(sentence, objects)
    plan = _normalise_plan(parsed, objects)
    return plan or _fallback_plan(sentence, objects)


async def plan_still_scene(sentence: str, objects: list[str]) -> dict:
    return await _direct(sentence, objects, 5, "image")


async def plan_animation(sentence: str, objects: list[str], duration: int = 5) -> dict:
    return await _direct(sentence, objects, duration, "video")
