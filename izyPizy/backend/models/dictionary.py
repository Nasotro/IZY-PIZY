from pydantic import BaseModel


class WordCreate(BaseModel):
    word: str


class WordOut(BaseModel):
    id: int
    word: str


class DictionaryEntry(BaseModel):
    number: str
    words: list[WordOut]
