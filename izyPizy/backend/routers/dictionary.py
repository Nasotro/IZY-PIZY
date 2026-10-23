from fastapi import APIRouter, Depends, HTTPException
from aiosqlite import Connection

import config
from database import get_db
from models.dictionary import DictionaryEntry, WordCreate, WordOut
from dependencies import CurrentUser, get_current_user

router = APIRouter()


@router.get("/dictionary", response_model=list[DictionaryEntry])
async def get_dictionary(
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_id = current_user.uid
    
    async with db.execute(
        "SELECT number FROM dictionary_numbers ORDER BY number"
    ) as cursor:
        numbers = [row["number"] async for row in cursor]

    # Left join on the lower-cased spelling so every entry sharing a word
    # (the same word can live under several numbers) shows the same icon.
    async with db.execute(
        """
        SELECT w.id, w.number, w.word, i.image_path AS icon_path
        FROM dictionary_words w
        LEFT JOIN word_icons i
               ON i.user_id = w.user_id
              AND i.word_key = lower(trim(w.word))
        WHERE w.user_id = ?
        ORDER BY w.id
        """,
        (user_id,),
    ) as cursor:
        rows = await cursor.fetchall()

    words_by_number: dict[str, list[WordOut]] = {n: [] for n in numbers}
    for row in rows:
        icon_path = row["icon_path"]
        words_by_number[row["number"]].append(
            WordOut(
                id=row["id"],
                word=row["word"],
                has_icon=bool(icon_path),
                icon_url=f"{config.IMAGE_BASE_URL}/{icon_path}" if icon_path else None,
            )
        )

    return [
        DictionaryEntry(number=num, words=words_by_number[num]) for num in numbers
    ]


@router.post("/dictionary/{number}/words", response_model=WordOut, status_code=201)
async def add_word(
    number: str,
    body: WordCreate,
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_id = current_user.uid
    
    async with db.execute(
        "SELECT number FROM dictionary_numbers WHERE number = ?", (number,)
    ) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail=f"Number '{number}' not found")

    word = body.word.strip()
    if not word:
        raise HTTPException(status_code=422, detail="word must not be empty")

    async with db.execute(
        "INSERT INTO dictionary_words (user_id, number, word) VALUES (?, ?, ?)",
        (user_id, number, word),
    ) as cursor:
        new_id = cursor.lastrowid
    await db.commit()
    return WordOut(id=new_id, word=word)


@router.put("/dictionary/words/{word_id}", response_model=WordOut)
async def update_word(
    word_id: int,
    body: WordCreate,
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_id = current_user.uid
    word = body.word.strip()
    if not word:
        raise HTTPException(status_code=422, detail="word must not be empty")

    async with db.execute(
        "SELECT id FROM dictionary_words WHERE id = ? AND user_id = ?", (word_id, user_id)
    ) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Word not found")

    await db.execute(
        "UPDATE dictionary_words SET word = ? WHERE id = ? AND user_id = ?",
        (word, word_id, user_id),
    )
    await db.commit()
    return WordOut(id=word_id, word=word)


@router.delete("/dictionary/words/{word_id}")
async def delete_word(
    word_id: int,
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_id = current_user.uid
    async with db.execute(
        "SELECT id FROM dictionary_words WHERE id = ? AND user_id = ?", (word_id, user_id)
    ) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Word not found")

    await db.execute("DELETE FROM dictionary_words WHERE id = ? AND user_id = ?", (word_id, user_id))
    await db.commit()
    return {"ok": True}
