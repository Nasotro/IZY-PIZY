from pydantic import BaseModel

# Image generation is now handled by the dedicated image_generation module
# Import here for backward compatibility
from models.image_generation import generate_image_from_prompt

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
    image_path: str | None = None
