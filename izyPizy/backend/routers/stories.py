from fastapi import APIRouter, Depends, HTTPException, Query
from aiosqlite import Connection

from database import get_db
from models.stories import StoryCreate, StoryOut

router = APIRouter()


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
):
    if position is not None:
        async with db.execute(
            "SELECT * FROM stories WHERE position = ? ORDER BY id",
            (position,),
        ) as cursor:
            rows = await cursor.fetchall()
    else:
        async with db.execute(
            "SELECT * FROM stories ORDER BY position, id"
        ) as cursor:
            rows = await cursor.fetchall()
    return [_row_to_story(r) for r in rows]


@router.post("/stories", response_model=StoryOut, status_code=201)
async def create_story(body: StoryCreate, db: Connection = Depends(get_db)):
    async with db.execute(
        """
        INSERT INTO stories (position, sentence, word_0, word_1, word_2, word_3, word_4)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (body.position, body.sentence, body.word_0, body.word_1, body.word_2, body.word_3, body.word_4),
    ) as cursor:
        new_id = cursor.lastrowid
    await db.commit()
    async with db.execute("SELECT * FROM stories WHERE id = ?", (new_id,)) as cursor:
        row = await cursor.fetchone()
    return _row_to_story(row)


@router.put("/stories/{story_id}", response_model=StoryOut)
async def update_story(story_id: int, body: StoryCreate, db: Connection = Depends(get_db)):
    async with db.execute("SELECT id FROM stories WHERE id = ?", (story_id,)) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Story not found")

    await db.execute(
        """
        UPDATE stories
        SET position = ?, sentence = ?, word_0 = ?, word_1 = ?, word_2 = ?, word_3 = ?, word_4 = ?
        WHERE id = ?
        """,
        (body.position, body.sentence, body.word_0, body.word_1, body.word_2, body.word_3, body.word_4, story_id),
    )
    await db.commit()
    async with db.execute("SELECT * FROM stories WHERE id = ?", (story_id,)) as cursor:
        row = await cursor.fetchone()
    return _row_to_story(row)


@router.delete("/stories/{story_id}")
async def delete_story(story_id: int, db: Connection = Depends(get_db)):
    async with db.execute("SELECT id FROM stories WHERE id = ?", (story_id,)) as cursor:
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Story not found")
    await db.execute("DELETE FROM stories WHERE id = ?", (story_id,))
    await db.commit()
    return {"ok": True}
