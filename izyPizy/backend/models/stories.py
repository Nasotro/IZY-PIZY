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
    video_path: str | None = None
    video_url: str | None = None
    start_frame_url: str | None = None
    end_frame_url: str | None = None
    visual_kind: str | None = None


# Request models for image generation
class VisualOptions(BaseModel):
    """Options for /stories/{id}/generate-visual (image or video)."""

    kind: str = "image"                      # "image" | "video"
    use_word_icons: bool = False             # feed the word icons as references
    num_images: int = 1                      # images only
    model: str = "big"                       # "small" | "big"
    width: int = 1024
    height: int = 1024
    use_mistral_enhancement: bool = True     # director / prompt enrichment
    auto_rephrase: bool = True
    custom_prompt: str | None = None
    timeout: int = 180
    duration: int = 5                        # video only, 5-20s
    draft: bool = True                       # video only, true = not billed
    resolution: str = "hd"                   # video only


class VisualResult(BaseModel):
    story: StoryOut
    kind: str
    images: list[dict] = []
    video_url: str | None = None
    start_frame_url: str | None = None
    end_frame_url: str | None = None
    plan: dict | None = None
    notes: list[str] = []


class ImageGenerationOptions(BaseModel):
    num_images: int = 1
    custom_prompt: Optional[str] = None
    use_mistral_enhancement: bool = False
    model: str = "big"
    width: int = 1024
    height: int = 1024
    timeout: int = 120
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
