from pydantic import BaseModel
from typing import Optional

# Image generation is now handled by the dedicated blackforest_image_generation module
# Import here for backward compatibility
from models.blackforest_image_generation import generate_image_from_prompt, BlackforestImageGenerator

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
    image_url: str | None = None


# Request models for image generation
class ImageGenerationOptions(BaseModel):
    num_images: int = 1
    custom_prompt: Optional[str] = None
    use_mistral_enhancement: bool = False
    model: str = "flux-2-pro"
    width: int = 1024
    height: int = 1024
    auto_rephrase: bool = True


class GeneratedImageInfo(BaseModel):
    path: str
    url: str | None = None


class BatchGenerationResponse(BaseModel):
    story_id: int
    images: list[GeneratedImageInfo]
    message: str | None = None


class PromptPreviewRequest(BaseModel):
    prompt: str
    key_elements: Optional[list[str]] = None


class PromptPreviewResponse(BaseModel):
    original_prompt: str
    enhanced_prompt: str
