from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from pydantic import BaseModel

from aiosqlite import Connection

import httpx

import uuid

from pathlib import Path



import config

from database import get_db

from models.stories import StoryCreate, StoryOut, ImageGenerationOptions

from dependencies import CurrentUser, get_current_user



router = APIRouter()



_pi_digits: str | None = None





def _get_pi_digits() -> str:

    global _pi_digits

    if _pi_digits is None:

        with open(config.PI_FILE, encoding="utf-8") as f:

            _pi_digits = "".join(ch for ch in f.read() if ch.isdigit())

    return _pi_digits





def _get_numbers_for_position(position: int) -> list[str]:

    digits = _get_pi_digits()

    start = position * 10

    if start + 10 > len(digits):

        raise HTTPException(

            status_code=400,

            detail=f"Position {position} exceeds available pi digits",

        )

    chunk = digits[start : start + 10]

    return [chunk[i : i + 2] for i in range(0, 10, 2)]





def _row_to_story(row) -> StoryOut:
    try:
        image_path = row["image_path"]
    except (KeyError, TypeError):
        image_path = None
    image_url = None
    if image_path:
        image_url = f"{config.IMAGE_BASE_URL}/{image_path}"
    return StoryOut(
        id=row["id"],
        position=row["position"],
        sentence=row["sentence"],
        word_0=row["word_0"],
        word_1=row["word_1"],
        word_2=row["word_2"],
        word_3=row["word_3"],
        word_4=row["word_4"],
        image_path=image_path,
        image_url=image_url,
    )





async def _ensure_image_dir() -> Path:

    """Ensure the image storage directory exists."""

    config.IMAGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    return config.IMAGE_STORAGE_DIR





@router.get("/stories", response_model=list[StoryOut])

async def get_stories(

    position: int | None = Query(default=None),

    db: Connection = Depends(get_db),

    current_user: CurrentUser = Depends(get_current_user),

):

    user_id = current_user.uid

    if position is not None:

        async with db.execute(

            "SELECT * FROM stories WHERE user_id = ? AND position = ? ORDER BY id",

            (user_id, position),

        ) as cursor:

            rows = await cursor.fetchall()

    else:

        async with db.execute(

            "SELECT * FROM stories WHERE user_id = ? ORDER BY position, id",

            (user_id,),

        ) as cursor:

            rows = await cursor.fetchall()

    return [_row_to_story(r) for r in rows]





async def _ensure_word_exists(db: Connection, user_id: str, number: str, word: str) -> None:

    word = word.strip()

    if not word:

        return

    async with db.execute(

        "SELECT id FROM dictionary_words WHERE user_id = ? AND number = ? AND word = ?",

        (user_id, number, word),

    ) as cursor:

        if await cursor.fetchone() is not None:

            return

    await db.execute(

        "INSERT INTO dictionary_words (user_id, number, word) VALUES (?, ?, ?)",

        (user_id, number, word),

    )





@router.post("/stories", response_model=StoryOut, status_code=201)

async def create_story(

    body: StoryCreate,

    db: Connection = Depends(get_db),

    current_user: CurrentUser = Depends(get_current_user),

):

    user_id = current_user.uid

    position = body.position

    if position is None:

        async with db.execute(

            "SELECT COALESCE(MAX(position), -1) + 1 AS next_position FROM stories WHERE user_id = ?",

            (user_id,),

        ) as cursor:

            row = await cursor.fetchone()

            position = row["next_position"]



    numbers = _get_numbers_for_position(position)

    words = [body.word_0, body.word_1, body.word_2, body.word_3, body.word_4]



    for number, word in zip(numbers, words):

        await _ensure_word_exists(db, user_id, number, word)

    await db.commit()



    async with db.execute(

        """

        INSERT INTO stories (user_id, position, sentence, word_0, word_1, word_2, word_3, word_4, image_path)

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)

        """,

        (user_id, position, body.sentence, body.word_0, body.word_1, body.word_2, body.word_3, body.word_4, None),

    ) as cursor:

        new_id = cursor.lastrowid

    await db.commit()

    async with db.execute(

        "SELECT * FROM stories WHERE id = ?", (new_id,)

    ) as cursor:

        row = await cursor.fetchone()

    return _row_to_story(row)





@router.put("/stories/{story_id}", response_model=StoryOut)

async def update_story(

    story_id: int,

    body: StoryCreate,

    db: Connection = Depends(get_db),

    current_user: CurrentUser = Depends(get_current_user),

):

    user_id = current_user.uid

    async with db.execute(

        "SELECT id FROM stories WHERE id = ? AND user_id = ?", (story_id, user_id)

    ) as cursor:

        if await cursor.fetchone() is None:

            raise HTTPException(status_code=404, detail="Story not found")



    await db.execute(

        """

        UPDATE stories

        SET position = ?, sentence = ?, word_0 = ?, word_1 = ?, word_2 = ?, word_3 = ?, word_4 = ?, image_path = image_path

        WHERE id = ? AND user_id = ?

        """,

        (body.position, body.sentence, body.word_0, body.word_1, body.word_2, body.word_3, body.word_4, story_id, user_id),

    )

    await db.commit()

    async with db.execute("SELECT * FROM stories WHERE id = ?", (story_id,)) as cursor:

        row = await cursor.fetchone()

    return _row_to_story(row)





@router.post("/stories/{story_id}/generate-image", response_model=StoryOut)

async def generate_story_image(

    story_id: int,

    width: int = Query(default=1024, ge=256, le=2048),

    height: int = Query(default=1024, ge=256, le=2048),

    model: str = Query(default="flux-2-pro"),

    use_mistral: bool = Query(default=False),

    timeout: int = Query(default=20, ge=1, le=1800),
    auto_rephrase: bool = Query(default=True),

    db: Connection = Depends(get_db),

    current_user: CurrentUser = Depends(get_current_user),

):

    """Generate an image for a story using Blackforest FLUX API, save and store it locally.
    
    Supports optional query parameters:
    - width: Image width in pixels (256-2048, default: 1024)
    - height: Image height in pixels (256-2048, default: 1024)
    - model: Blackforest model to use (default: flux-2-pro)
    - use_mistral: Whether to enhance prompt with Mistral (default: False)
    - timeout: Maximum wait time in seconds (1-1800, default: 20)
    - auto_rephrase: Whether to automatically rephrase prompts that trigger moderation (default: True)
    """

    from models.blackforest_image_generation import generate_image_from_prompt

    

    user_id = current_user.uid

    

    # Get the story

    async with db.execute(

        "SELECT * FROM stories WHERE id = ? AND user_id = ?", (story_id, user_id)

    ) as cursor:

        row = await cursor.fetchone()

        if row is None:

            raise HTTPException(status_code=404, detail="Story not found")

    

    story = _row_to_story(row)

    

    # Check if story has a sentence to use as prompt

    if not story.sentence:

        raise HTTPException(

            status_code=400,

            detail="Story has no sentence to generate image from"

        )

    

    # Check if Blackforest API key is configured (not required in local mode)
    if not config.BFL_API_KEY and not config.LOCAL_MODE:

        raise HTTPException(

            status_code=500,

            detail="Blackforest API key not configured"

        )

    

    try:

        # Step 1: Generate image using Blackforest FLUX API

        image_dir = await _ensure_image_dir()

        image_filename = f"story_{story_id}_{uuid.uuid4().hex}.png"

        image_path = image_dir / image_filename

        

        # Pass the 5 important words as key_elements
        key_elements = [story.word_0, story.word_1, story.word_2, story.word_3, story.word_4]
        # Filter out empty strings
        key_elements = [w for w in key_elements if w and w.strip()]
        
        await generate_image_from_prompt(
            story.sentence, 
            str(image_path),
            width=width,
            height=height,
            model=model,
            use_mistral_enhancement=use_mistral,
            timeout=timeout,
            auto_rephrase=auto_rephrase,
            key_elements=key_elements if key_elements else None
        )

        

        # Step 2: Store relative path in database

        relative_path = image_filename

        await db.execute(

            "UPDATE stories SET image_path = ? WHERE id = ? AND user_id = ?",

            (relative_path, story_id, user_id),

        )

        await db.commit()

        

        # Step 3: Return updated story

        async with db.execute(

            "SELECT * FROM stories WHERE id = ?", (story_id,)

        ) as cursor:

            row = await cursor.fetchone()

        return _row_to_story(row)

        

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=f"Failed to generate image: {str(e)}"

        )





@router.delete("/stories/{story_id}")

async def delete_story(

    story_id: int,

    db: Connection = Depends(get_db),

    current_user: CurrentUser = Depends(get_current_user),

):

    user_id = current_user.uid

    

    # Get image path before deleting

    image_path = None

    async with db.execute(

        "SELECT image_path FROM stories WHERE id = ? AND user_id = ?", (story_id, user_id)

    ) as cursor:

        row = await cursor.fetchone()

        if row is None:

            raise HTTPException(status_code=404, detail="Story not found")

        image_path = row["image_path"] if "image_path" in row else None

    

    # Delete from database

    await db.execute("DELETE FROM stories WHERE id = ? AND user_id = ?", (story_id, user_id))

    await db.commit()

    

    # Delete image file if it exists

    if image_path:

        try:

            (config.IMAGE_STORAGE_DIR / image_path).unlink(missing_ok=True)

        except Exception:

            pass  # Best effort cleanup

    

    return {"ok": True}


@router.post("/stories/{story_id}/generate-image-batch")
async def generate_story_image_batch(
    story_id: int,
    options: Optional[dict] = None,
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Generate multiple images for a story with custom options."""
    from models.blackforest_image_generation import generate_image_from_prompt
    user_id = current_user.uid
    async with db.execute(
        "SELECT * FROM stories WHERE id = ? AND user_id = ?", (story_id, user_id)
    ) as cursor:
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Story not found")
    story = _row_to_story(row)
    if not story.sentence:
        raise HTTPException(status_code=400, detail="Story has no sentence to generate image from")
    if not config.BFL_API_KEY and not config.LOCAL_MODE:
        raise HTTPException(status_code=500, detail="Blackforest API key not configured")
    if options is None:
        options = {}
    num_images = min(max(options.get('num_images', 1), 1), 10)
    use_mistral = options.get('use_mistral_enhancement', False)
    model = options.get('model', 'flux-2-pro')
    width = options.get('width', 1024)
    height = options.get('height', 1024)
    auto_rephrase = options.get('auto_rephrase', True)
    prompt = options.get('custom_prompt') or story.sentence
    key_elements = [story.word_0, story.word_1, story.word_2, story.word_3, story.word_4]
    key_elements = [w for w in key_elements if w and w.strip()] or None
    try:
        image_dir = await _ensure_image_dir()
        generated_images = []
        for i in range(num_images):
            image_filename = f"story_{story_id}_{uuid.uuid4().hex}.png"
            image_path = image_dir / image_filename
            await generate_image_from_prompt(
                prompt, str(image_path), width=width, height=height,
                model=model, use_mistral_enhancement=use_mistral, 
                auto_rephrase=auto_rephrase, key_elements=key_elements
            )
            relative_path = image_filename
            image_url = f"{config.IMAGE_BASE_URL}/{relative_path}"
            generated_images.append({"path": relative_path, "url": image_url})
        if generated_images:
            await db.execute(
                "UPDATE stories SET image_path = ? WHERE id = ? AND user_id = ?",
                (generated_images[0]["path"], story_id, user_id),
            )
            await db.commit()
        return {"story_id": story_id, "images": generated_images, "message": f"Generated {len(generated_images)} images"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate images: {str(e)}")


class SetImageRequest(BaseModel):
    image_path: str


@router.post("/stories/{story_id}/set-image", response_model=StoryOut)
async def set_story_image(
    story_id: int,
    request: SetImageRequest,
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Set the image path for a story after batch generation."""
    user_id = current_user.uid
    image_path = request.image_path
    
    # Verify the story exists and belongs to the user
    async with db.execute(
        "SELECT id FROM stories WHERE id = ? AND user_id = ?", (story_id, user_id)
    ) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Story not found")
    
    # Update the image path
    await db.execute(
        "UPDATE stories SET image_path = ? WHERE id = ? AND user_id = ?",
        (image_path, story_id, user_id),
    )
    await db.commit()
    
    # Return the updated story
    async with db.execute("SELECT * FROM stories WHERE id = ?", (story_id,)) as cursor:
        row = await cursor.fetchone()
    
    return _row_to_story(row)


@router.post("/stories/preview-prompt")
async def preview_enhanced_prompt(request: Optional[dict] = None):
    """Get a preview of how the prompt will be enhanced by Mistral."""
    try:
        from models.blackforest_image_generation import BlackforestImageGenerator
        if request is None:
            return {"error": "No prompt provided"}
        prompt = request.get('prompt', '')
        key_elements = request.get('key_elements')
        generator = BlackforestImageGenerator(api_key=config.BFL_API_KEY)
        enhanced = await generator.enhance_prompt_with_mistral(prompt, key_elements)
        return {"original_prompt": prompt, "enhanced_prompt": enhanced}
    except Exception as e:
        if request:
            return {"original_prompt": request.get('prompt', ''), "enhanced_prompt": request.get('prompt', '')}
        return {"error": str(e)}

