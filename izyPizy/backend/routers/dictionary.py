from fastapi import APIRouter, Depends, HTTPException
from aiosqlite import Connection

from database import get_db
from models.dictionary import DictionaryEntry, WordCreate, WordOut

router = APIRouter()


@router.get("/dictionary", response_model=list[DictionaryEntry])
async def get_dictionary(db: Connection = Depends(get_db)):
    # Fetch all numbers
    async with db.execute(
        "SELECT number FROM dictionary_numbers ORDER BY number"
    ) as cursor:
        numbers = [row["number"] async for row in cursor]

    # Fetch all words
    async with db.execute(
        "SELECT id, number, word FROM dictionary_words ORDER BY id"
    ) as cursor:
        rows = await cursor.fetchall()

    words_by_number: dict[str, list[WordOut]] = {n: [] for n in numbers}
    for row in rows:
        words_by_number[row["number"]].append(WordOut(id=row["id"], word=row["word"]))

    return [
        DictionaryEntry(number=num, words=words_by_number[num]) for num in numbers
    ]


@router.post("/dictionary/{number}/words", response_model=WordOut, status_code=201)
async def add_word(number: str, body: WordCreate, db: Connection = Depends(get_db)):
    # Validate number exists
    async with db.execute(
        "SELECT number FROM dictionary_numbers WHERE number = ?", (number,)
    ) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail=f"Number '{number}' not found")

    word = body.word.strip()
    if not word:
        raise HTTPException(status_code=422, detail="word must not be empty")

    async with db.execute(
        "INSERT INTO dictionary_words (number, word) VALUES (?, ?)", (number, word)
    ) as cursor:
        new_id = cursor.lastrowid
    await db.commit()
    return WordOut(id=new_id, word=word)


@router.put("/dictionary/words/{word_id}", response_model=WordOut)
async def update_word(word_id: int, body: WordCreate, db: Connection = Depends(get_db)):
    word = body.word.strip()
    if not word:
        raise HTTPException(status_code=422, detail="word must not be empty")

    async with db.execute(
        "SELECT id FROM dictionary_words WHERE id = ?", (word_id,)
    ) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Word not found")

    await db.execute(
        "UPDATE dictionary_words SET word = ? WHERE id = ?", (word, word_id)
    )
    await db.commit()
    return WordOut(id=word_id, word=word)


@router.delete("/dictionary/words/{word_id}")
async def delete_word(word_id: int, db: Connection = Depends(get_db)):
    async with db.execute(
        "SELECT id FROM dictionary_words WHERE id = ?", (word_id,)
    ) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Word not found")

    await db.execute("DELETE FROM dictionary_words WHERE id = ?", (word_id,))
    await db.commit()
    return {"ok": True}
