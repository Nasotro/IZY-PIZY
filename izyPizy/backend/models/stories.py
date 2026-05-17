from pydantic import BaseModel
import asyncio


async def generate_image_from_prompt(prompt: str, output_path: str = "generated_image.png") -> str:
    from google import genai
    from PIL import Image

    def _run_generate() -> str:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[prompt],
        )

        parts = getattr(response, "parts", None)
        if not parts and getattr(response, "candidates", None):
            parts = response.candidates[0].content.parts

        if not parts:
            raise RuntimeError("No image was generated from the prompt")

        for part in parts:
            if getattr(part, "inline_data", None) is not None:
                image = part.as_image()
                image.save(output_path)
                return output_path

        raise RuntimeError("No image was generated from the prompt")

    return await asyncio.to_thread(_run_generate)

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
