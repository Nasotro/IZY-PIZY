from pydantic import BaseModel


class StoryCreate(BaseModel):
    position: int | None = None
    sentence: str | None = None
    word_0: str
    word_1: str
    word_2: str
    word_3: str
    word_4: str


class StoryOut(BaseModel):
    id: int
    position: int
    sentence: str | None
    word_0: str
    word_1: str
    word_2: str
    word_3: str
    word_4: str
