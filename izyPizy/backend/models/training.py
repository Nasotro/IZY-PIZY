from pydantic import BaseModel


class VerifyRequest(BaseModel):
    position: int
    digit: str


class VerifyResponse(BaseModel):
    correct: bool
    expected: str
    position: int
