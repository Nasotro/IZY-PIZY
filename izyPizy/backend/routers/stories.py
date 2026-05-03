from fastapi import APIRouter, Depends, HTTPException, Query
from aiosqlite import Connection

import config
from database import get_db
from models.stories import StoryCreate, StoryOut
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
    return StoryOut(
        id=row["id"],
        position=row["position"],
        sentence=row["sentence"],
        word_0=row["word_0"],
        word_1=row["word_1"],
        word_2=row["word_2"],
        word_3=row["word_3"],
        word_4=row["word_4"],
    )


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


async def _ensure_word_exists(db: Connection, number: str, word: str) -> None:
    word = word.strip()
    if not word:
        return
    async with db.execute(
        "SELECT id FROM dictionary_words WHERE number = ? AND word = ?",
        (number, word),
    ) as cursor:
        if await cursor.fetchone() is not None:
            return
    await db.execute(
        "INSERT INTO dictionary_words (number, word) VALUES (?, ?)",
        (number, word),
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
        await _ensure_word_exists(db, number, word)
    await db.commit()

    async with db.execute(
        """
        INSERT INTO stories (user_id, position, sentence, word_0, word_1, word_2, word_3, word_4)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, position, body.sentence, body.word_0, body.word_1, body.word_2, body.word_3, body.word_4),
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
        SET position = ?, sentence = ?, word_0 = ?, word_1 = ?, word_2 = ?, word_3 = ?, word_4 = ?
        WHERE id = ? AND user_id = ?
        """,
        (body.position, body.sentence, body.word_0, body.word_1, body.word_2, body.word_3, body.word_4, story_id, user_id),
    )
    await db.commit()
    async with db.execute("SELECT * FROM stories WHERE id = ?", (story_id,)) as cursor:
        row = await cursor.fetchone()
    return _row_to_story(row)


@router.delete("/stories/{story_id}")
async def delete_story(
    story_id: int,
    db: Connection = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    user_id = current_user.uid
    async with db.execute(
        "SELECT id FROM stories WHERE id = ? AND user_id = ?", (story_id, user_id)
    ) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Story not found")
    await db.execute("DELETE FROM stories WHERE id = ? AND user_id = ?", (story_id, user_id))
    await db.commit()
    return {"ok": True}
