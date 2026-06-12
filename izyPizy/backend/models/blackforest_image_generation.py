"""Image generation module using Blackforest Labs FLUX API."""
import asyncio
import aiohttp
import httpx
import json
from pathlib import Path
from typing import Optional
import config


class BlackforestImageGenerator:
    """Handles image generation using Blackforest Labs FLUX API."""
    
    def __init__(self, api_key: str):
        """Initialize the Blackforest client with API key."""
        self.api_key = api_key
        self.base_url = "https://api.bfl.ai/v1"
        self.default_model = "flux-2-pro-preview"
    
    async def generate_image(
        self,
        prompt: str,
        output_path: str,
        width: int = 1024,
        height: int = 1024,
        model: str = None,
        use_mistral_enhancement: bool = True,
        timeout: float = 300.0
    ) -> str:
        """
        Generate an image from a text prompt using Blackforest FLUX API and save it locally.
        
        Args:
            prompt: The text prompt to generate an image from
            output_path: Path where the generated image will be saved
            width: Width of the generated image in pixels
            height: Height of the generated image in pixels
            model: Blackforest model identifier (default: flux-2-pro-preview)
            use_mistral_enhancement: Whether to enhance the prompt using Mistral LLM
            timeout: Maximum time to wait for image generation in seconds
            
        Returns:
            The output path where the image was saved
            
        Raises:
            RuntimeError: If image generation fails
        """
        # Use default model if not specified
        if model is None:
            model = self.default_model
        
        # Optionally enhance the prompt using Mistral
        if use_mistral_enhancement:
            enhanced_prompt = await self.enhance_prompt_with_mistral(prompt)
        else:
            enhanced_prompt = prompt
        
        # Step 1: Submit generation request to Blackforest API
        request_url = f"{self.base_url}/{model}"
        
        headers = {
            "accept": "application/json",
            "x-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": enhanced_prompt,
            "width": width,
            "height": height
        }
        
        try:
            # Submit the request
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    request_url,
                    headers=headers,
                    json=payload
                )
            
            if response.status_code != 200:
                raise RuntimeError(f"Failed to submit image generation: HTTP {response.status_code} - {response.text}")
            
            request_data = response.json()
            
            # Extract polling URL
            if "polling_url" not in request_data:
                raise RuntimeError(f"Unexpected response format: {json.dumps(request_data)}")
            
            polling_url = request_data["polling_url"]
            request_id = request_data.get("id", "unknown")
            
            # Step 2: Poll for results
            import time
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                await asyncio.sleep(0.5)  # Wait before polling
                
                # Poll for the result
                async with httpx.AsyncClient(timeout=60.0) as client:
                    poll_response = await client.get(
                        polling_url,
                        headers={
                            "accept": "application/json",
                            "x-key": self.api_key
                        }
                    )
                
                if poll_response.status_code != 200:
                    raise RuntimeError(f"Failed to poll for results: HTTP {poll_response.status_code} - {poll_response.text}")
                
                poll_data = poll_response.json()
                status = poll_data.get("status")
                
                if status == "Ready":
                    # Image is ready, download it
                    if "result" not in poll_data or "sample" not in poll_data.get("result", {}):
                        raise RuntimeError(f"Unexpected result format: {json.dumps(poll_data)}")
                    
                    image_url = poll_data["result"]["sample"]
                    await self._download_image(image_url, output_path)
                    return output_path
                
                elif status in ["Error", "Failed"]:
                    raise RuntimeError(f"Image generation failed: {json.dumps(poll_data)}")
                
                # Still processing, continue polling
                # Optional: print progress
                # print(f"Request {request_id}: {status}")
            
            # Timeout
            raise RuntimeError(f"Image generation timed out after {timeout} seconds")
            
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
    async def enhance_prompt_with_mistral(story_sentence: str) -> str:
        """
        Enhance a story sentence into a detailed, descriptive prompt using Mistral LLM.
        
        Transforms a simple story sentence into a rich, detailed prompt that will
        generate better images by providing more context, style, and visual details.
        
        Args:
            story_sentence: The original story sentence from the user
            
        Returns:
            An enhanced prompt optimized for image generation
            
        Example:
            Input: "A cat on a roof"
            Output: "A beautiful orange tabby cat with green eyes sitting gracefully 
                     on a red tiled roof at sunset, warm golden light, detailed fur 
                     texture, cinematic composition, digital art style"
        """
        # System prompt for Mistral to enhance the story
        system_prompt = """You are an expert in transforming short story sentences into highly detailed, 
vivid descriptions for AI image generation. Your goal is to expand a simple sentence 
into a rich, comprehensive prompt that will help an AI image generator create the 
best possible illustration.

Guidelines:
1. Preserve the core meaning and main elements of the original sentence
2. Add sensory details: colors, textures, lighting, atmosphere
3. Include style suggestions (digital art, watercolor, cinematic, etc.)
4. Add composition and perspective details
5. Include mood and emotional tone
6. Keep it under 200 words
7. Always respond in English, even if the input is in another language
8. Use descriptive, evocative language
9. Add visual details that make the scene more interesting
10. Avoid negative prompts (what NOT to include)

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

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers=headers,
                    json=payload
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
_blackforest_generator: Optional[BlackforestImageGenerator] = None


async def get_blackforest_generator(api_key: str) -> BlackforestImageGenerator:
    """
    Get or create the global Blackforest image generator instance.
    
    Args:
        api_key: Blackforest API key
        
    Returns:
        BlackforestImageGenerator instance
    """
    global _blackforest_generator
    if _blackforest_generator is None:
        _blackforest_generator = BlackforestImageGenerator(api_key=api_key)
    return _blackforest_generator


async def generate_image_from_prompt(
    prompt: str,
    output_path: str,
    width: int = 1024,
    height: int = 1024,
    model: str = None,
    use_mistral_enhancement: bool = True
) -> str:
    """
    Generate an image from a text prompt using Blackforest FLUX API.
    
    This is a convenience function that uses the global image generator.
    
    Args:
        prompt: The text prompt to generate an image from
        output_path: Path where the generated image will be saved
        width: Width of the generated image in pixels
        height: Height of the generated image in pixels
        model: Blackforest model identifier (default: flux-2-pro-preview)
        use_mistral_enhancement: Whether to enhance the prompt using Mistral LLM (default: True)
        
    Returns:
        The output path where the image was saved
    """
    generator = await get_blackforest_generator(config.BFL_API_KEY)
    return await generator.generate_image(
        prompt,
        output_path,
        width,
        height,
        model,
        use_mistral_enhancement
    )
