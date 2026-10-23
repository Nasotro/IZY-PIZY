from pydantic import BaseModel


class WordCreate(BaseModel):
    word: str


class WordOut(BaseModel):
    id: int
    word: str
    has_icon: bool = False
    icon_url: str | None = None


class DictionaryEntry(BaseModel):
    number: str
    words: list[WordOut]
