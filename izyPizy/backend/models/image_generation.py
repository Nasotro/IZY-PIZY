"""Image generation module using Runware SDK."""
import asyncio
import aiohttp
import httpx
import json
from pathlib import Path
from typing import Optional

from runware import Runware, IImageInference
import config


class ImageGenerator:
    """Handles image generation using Runware SDK."""
    
    def __init__(self, api_key: str):
        """Initialize the Runware client with API key."""
        self.api_key = api_key
        self._runware: Optional[Runware] = None
    
    async def connect(self) -> None:
        """Connect to Runware API."""
        if self._runware is None:
            self._runware = Runware(api_key=self.api_key)
            await self._runware.connect()
    
    async def ensure_connected(self) -> Runware:
        """Ensure connection to Runware and return the client."""
        if self._runware is None:
            await self.connect()
        return self._runware
    
    async def generate_image(
        self,
        prompt: str,
        output_path: str,
        width: int = 1024,
        height: int = 1024,
        model: str = "runware:101@1",
        use_mistral_enhancement: bool = True,
        key_elements: list[str] | None = None
    ) -> str:
        """
        Generate an image from a text prompt and save it to the specified path.
        
        Args:
            prompt: The text prompt to generate an image from
            output_path: Path where the generated image will be saved
            width: Width of the generated image in pixels
            height: Height of the generated image in pixels
            model: Runware model identifier
            use_mistral_enhancement: Whether to enhance the prompt using Mistral LLM
            key_elements: List of 3-5 important words/objects that MUST appear prominently
            
        Returns:
            The output path where the image was saved
            
        Raises:
            RuntimeError: If image generation fails
        """
        # Optionally enhance the prompt using Mistral
        if use_mistral_enhancement:
            enhanced_prompt = await self.enhance_prompt_with_mistral(prompt, key_elements)
        else:
            enhanced_prompt = prompt
        
        runware = await self.ensure_connected()
        
        request = IImageInference(
            positivePrompt=enhanced_prompt,
            model=model,
            width=width,
            height=height
        )
        
        try:
            # Generate image via Runware API
            images = await runware.imageInference(requestImage=request)
            
            if not images or not images[0].imageURL:
                raise RuntimeError("No image was generated from the prompt")
            
            # Download the generated image
            image_url = images[0].imageURL
            await self._download_image(image_url, output_path)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate image: {str(e)}")
    
    async def _download_image(self, url: str, output_path: str) -> None:
        """Download an image from a URL and save it locally."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to download image: HTTP {response.status}")
                
                content = await response.read()
                Path(output_path).write_bytes(content)

    @staticmethod
    async def enhance_prompt_with_mistral(
        story_sentence: str,
        key_elements: list[str] | None = None
    ) -> str:
        """
        Enhance a story sentence into a detailed, descriptive prompt using Mistral LLM.
        
        Transforms a simple story sentence into a rich, detailed prompt that will
        generate better images by providing more context, style, and visual details.
        
        Args:
            story_sentence: The original story sentence from the user
            key_elements: List of 3-5 important words/objects that MUST appear prominently.
                          If provided, these will be explicitly emphasized in the enhanced prompt.
            
        Returns:
            An enhanced prompt optimized for image generation
            
        Example:
            Input: "A cat on a roof"
            Output: "A beautiful orange tabby cat with green eyes sitting gracefully 
                     on a red tiled roof at sunset, warm golden light, detailed fur 
                     texture, cinematic composition, digital art style"
        """
        # Build system prompt with key elements if provided
        if key_elements and len(key_elements) > 0:
            key_elements_str = ", ".join(key_elements).upper()
            key_clause = f"IMPORTANT: These key elements MUST all be clearly visible and prominent: {key_elements_str}"
        else:
            key_clause = ""

        # System prompt for Mistral to enhance the story
        system_prompt = f"""You are an expert in transforming short story sentences into highly detailed, 
vivid descriptions for AI image generation. Your goal is to expand a simple sentence 
into a rich, comprehensive prompt that will help an AI image generator create the 
best possible illustration.

{key_clause}

Guidelines:
1. Preserve the core meaning and ALL main elements of the original sentence
2. Explicitly describe each key element with rich visual details
3. Ensure all key elements are clearly visible and positioned prominently in the composition
4. Add sensory details: colors, textures, lighting, atmosphere
5. Include style suggestions (digital art, watercolor, cinematic, etc.)
6. Add composition and perspective details
7. Include mood and emotional tone
8. Keep it under 200 words
9. Always respond in English, even if the input is in another language
10. Use descriptive, evocative language
11. Add visual details that make the scene more interesting
12. Avoid negative prompts (what NOT to include)

Return only the enhanced prompt, nothing else."""

        user_prompt = f"""Please enhance this story sentence for image generation:

{story_sentence}

Enhanced prompt:"""

        try:
            # Use Mistral API
            api_key = config.MISTRAL_API_KEY
            if not api_key:
                # Fallback: return the original sentence if no API key
                return story_sentence

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "mistral-tiny",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 200
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    enhanced_prompt = data["choices"][0]["message"]["content"].strip()
                    # Remove any quotes or markdown formatting
                    enhanced_prompt = enhanced_prompt.strip('"\'\n')
                    return enhanced_prompt
                else:
                    print(f"Mistral API error: {response.status_code} - {response.text}")
                    # Fallback to original sentence
                    return story_sentence

        except Exception as e:
            print(f"Error enhancing prompt with Mistral: {str(e)}")
            # Fallback to original sentence
            return story_sentence


# Global image generator instance (will be initialized with API key)
_image_generator: Optional[ImageGenerator] = None


async def get_image_generator(api_key: str) -> ImageGenerator:
    """
    Get or create the global image generator instance.
    
    Args:
        api_key: Runware API key
        
    Returns:
        ImageGenerator instance
    """
    global _image_generator
    if _image_generator is None:
        _image_generator = ImageGenerator(api_key=api_key)
        await _image_generator.connect()
    return _image_generator


async def generate_image_from_prompt(
    prompt: str,
    output_path: str,
    width: int = 1024,
    height: int = 1024,
    model: str = "runware:101@1",
    use_mistral_enhancement: bool = True,
    key_elements: list[str] | None = None
) -> str:
    """
    Generate an image from a text prompt using Runware.
    
    This is a convenience function that uses the global image generator.
    
    Args:
        prompt: The text prompt to generate an image from
        output_path: Path where the generated image will be saved
        width: Width of the generated image in pixels
        height: Height of the generated image in pixels
        model: Runware model identifier
        use_mistral_enhancement: Whether to enhance the prompt using Mistral LLM (default: True)
        key_elements: List of 3-5 important words/objects that MUST appear prominently
        
    Returns:
        The output path where the image was saved
    """
    generator = await get_image_generator(config.RUNWARE_API_KEY)
    return await generator.generate_image(
        prompt, 
        output_path, 
        width, 
        height, 
        model,
        use_mistral_enhancement,
        key_elements
    )
