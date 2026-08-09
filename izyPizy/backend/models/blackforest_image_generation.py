"""Image generation module using Blackforest Labs FLUX API."""
import asyncio
import aiohttp
import httpx
import json
import time
from pathlib import Path
from typing import Optional
import config


class BlackforestImageGenerator:
    """Handles image generation using Blackforest Labs FLUX API."""
    
    def __init__(self, api_key: str, base_url: str = None):
        """Initialize the Blackforest client with API key.
        
        Args:
            api_key: Blackforest API key
            base_url: Optional custom base URL (e.g., for regional endpoints)
                      Default: https://api.bfl.ai/v1
        """
        self.api_key = api_key
        self.base_url = base_url or "https://api.bfl.ai/v1"
        self.default_model = "flux-2-pro"
        print(f"[DEBUG] BlackforestImageGenerator initialized with base_url: {self.base_url}")
    
    async def generate_image(
        self,
        prompt: str,
        output_path: str,
        width: int = 1024,
        height: int = 1024,
        model: str = None,
        use_mistral_enhancement: bool = False,
        timeout: float = 20.0,
        key_elements: list[str] | None = None,
        auto_rephrase: bool = True
    ) -> str:
        """
        Generate an image from a text prompt using Blackforest FLUX API and save it locally.
        
        Args:
            prompt: The text prompt to generate an image from
            output_path: Path where the generated image will be saved
            width: Width of the generated image in pixels
            height: Height of the generated image in pixels
            model: Blackforest model identifier (default: flux-2-pro)
            use_mistral_enhancement: Whether to enhance the prompt using Mistral LLM
            timeout: Maximum time to wait for image generation in seconds
            key_elements: List of 3-5 important words/objects that MUST appear prominently
            auto_rephrase: Whether to automatically rephrase prompts that trigger moderation (default: True)
            
        Returns:
            The output path where the image was saved
            
        Raises:
            RuntimeError: If image generation fails
        """
        # Use default model if not specified
        if model is None:
            model = self.default_model
        
        start_time = time.time()
        tried_prompts = []
        
        # Optionally enhance the prompt using Mistral
        if use_mistral_enhancement:
            enhanced_prompt = await self.enhance_prompt_with_mistral(prompt, key_elements)
        else:
            enhanced_prompt = prompt
        
        # Main retry loop - will retry with rephrased prompts if moderation errors occur
        while time.time() - start_time < timeout:
            request_url = f"{self.base_url}/{model}"
            print(f"[DEBUG] Generating with model {model} at URL: {request_url}")
            
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
            
            print(f"[DEBUG] Sending payload with prompt length={len(enhanced_prompt)}, prompt_preview={enhanced_prompt[:100]}")
            
            try:
                # Submit the request
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        request_url,
                        headers=headers,
                        json=payload
                    )
                
                # Debug: Show response details
                print(f"[DEBUG] POST response status={response.status_code}, text={response.text[:200]}")
                
                if response.status_code != 200:
                    # Check for specific errors
                    if response.status_code == 401:
                        raise RuntimeError(
                            f"Invalid API key. Please check your BFL_API_KEY. "
                            f"Get a valid key at https://dashboard.bfl.ai/"
                        )
                    elif response.status_code == 402:
                        raise RuntimeError(
                            f"Out of credits. Please add credits at https://dashboard.bfl.ai/"
                        )
                    elif response.status_code == 429:
                        raise RuntimeError(
                            f"Rate limited. Please wait and try again. "
                            f"You have a limit of 24 active tasks."
                        )
                    else:
                        # For other errors, raise immediately
                        raise RuntimeError(f"Failed to submit image generation: HTTP {response.status_code} - {response.text}")
                
                request_data = response.json()
                
                # Extract polling URL
                if "polling_url" not in request_data:
                    raise RuntimeError(f"Unexpected response format: {json.dumps(request_data)}")
                
                polling_url = request_data["polling_url"]
                request_id = request_data.get("id", "unknown")
                
                # Poll for results
                model_start_time = time.time()
                poll_interval = 2.0
                remaining_timeout = timeout - (time.time() - start_time)
                
                async with httpx.AsyncClient(timeout=60.0) as poll_client:
                    while time.time() - model_start_time < remaining_timeout:
                        await asyncio.sleep(poll_interval)
                        
                        # Poll for the result
                        poll_response = await poll_client.get(
                            polling_url,
                            headers={
                                "accept": "application/json",
                                "x-key": self.api_key
                            }
                        )
                        
                        print(f"[DEBUG] POLL response status={poll_response.status_code}, status_field={poll_response.json().get('status')}, text={poll_response.text[:200]}")
                        
                        if poll_response.status_code != 200:
                            raise RuntimeError(f"Failed to poll for results: HTTP {poll_response.status_code} - {poll_response.text}")
                        
                        poll_data = poll_response.json()
                        status = poll_data.get("status")
                        
                        # Log progress for debugging
                        elapsed = int(time.time() - model_start_time)
                        print(f"[{model}] Request {request_id}: status={status} ({elapsed}s)")
                        
                        if status == "Ready":
                            # Image is ready, download it
                            if "result" not in poll_data or "sample" not in poll_data.get("result", {}):
                                raise RuntimeError(f"Unexpected result format: {json.dumps(poll_data)}")
                            
                            image_url = poll_data["result"]["sample"]
                            await self._download_image(image_url, output_path)
                            return output_path
                        
                        elif status in ["Error", "Failed", "Request Moderated"]:
                            # Check if this is a moderation error
                            error_text = json.dumps(poll_data)
                            is_moderation_error = (
                                "Request Moderated" in error_text or
                                "Moderation" in error_text or
                                "Protected Content" in error_text or
                                "copyright" in error_text.lower() or
                                "trademark" in error_text.lower()
                            )
                            
                            if is_moderation_error:
                                raise RuntimeError(f"Moderation error: {json.dumps(poll_data)}")
                            else:
                                raise RuntimeError(f"Image generation failed: {json.dumps(poll_data)}")
                        
                        # Still processing, continue polling
                    
                    # Timeout
                    elapsed_model = time.time() - model_start_time
                    raise RuntimeError(f"Image generation timed out after {elapsed_model:.1f}s (limit: {remaining_timeout:.1f}s) for model {model}")
            
            except Exception as e:
                error_str = str(e)
                
                # Check if this is a moderation error and we can rephrase
                is_moderation_error = (
                    "Request Moderated" in error_str or
                    "Moderation" in error_str or
                    "Protected Content" in error_str or
                    "copyright" in error_str.lower() or
                    "trademark" in error_str.lower()
                )
                
                # Check if we've tried this prompt before
                current_prompt_key = enhanced_prompt[:100]
                
                if is_moderation_error and auto_rephrase and current_prompt_key not in tried_prompts:
                    # Mark this prompt as tried
                    tried_prompts.append(current_prompt_key)
                    
                    # Try to rephrase the prompt to avoid copyrighted content
                    print(f"[DEBUG] Moderation error detected, rephrasing prompt: '{enhanced_prompt[:80]}...'")
                    if use_mistral_enhancement:
                        rephrased = await self.rephrase_to_avoid_copyright(enhanced_prompt, key_elements)
                    else:
                        rephrased = await self.rephrase_to_avoid_copyright(prompt, key_elements)
                    
                    # If rephrasing gives us the same prompt, we can't improve it
                    if rephrased == enhanced_prompt or rephrased == prompt:
                        print(f"[DEBUG] Rephrasing didn't change the prompt, cannot avoid moderation")
                        raise RuntimeError(f"Moderation error and prompt cannot be rephrased: {error_str}")
                    
                    # Use the rephrased prompt and retry with the same model
                    enhanced_prompt = rephrased
                    print(f"[DEBUG] Retrying with rephrased prompt: '{rephrased[:80]}...'")
                    continue
                
                # Not a moderation error or can't rephrase - raise the error
                raise RuntimeError(f"Failed to generate image: {error_str}")
        
        # Overall timeout
        raise RuntimeError(f"Image generation timed out after {timeout} seconds")
    
    async def _download_image(self, url: str, output_path: str) -> None:
        """Download an image from a URL and save it locally."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise RuntimeError(f"Failed to download image: HTTP {response.status}")
                
                content = await response.read()
                Path(output_path).write_bytes(content)
    
    @staticmethod
    async def rephrase_to_avoid_copyright(
        prompt: str,
        key_elements: list[str] | None = None
    ) -> str:
        """
        Rephrase a prompt to avoid copyrighted/trademarked content using Mistral LLM.
        
        This is used when Blackforest API returns moderation errors due to protected content.
        It replaces copyrighted characters, brands, and trademarks with generic equivalents.
        
        Args:
            prompt: The original prompt that was moderated
            key_elements: List of key elements that should be preserved (but made generic)
            
        Returns:
            A rephrased prompt that avoids copyrighted content
            
        Example:
            Input: "Luffy walking in Nice listening to rare rap"
            Output: "A young adventurer with a straw hat walking in a Mediterranean city listening to music"
        """
        # Build list of known copyrighted terms to avoid
        copyrighted_terms = [
            "Luffy", "Monkey D. Luffy", "One Piece", "Straw Hat", "Gear 5", "Haki",
            "Naruto", "Sasuke", "Sakura", "Kakashi", "Dragon Ball", "Goku", "Vegeta",
            "Attack on Titan", "Eren", "Mikasa", "Armin", "Demon Slayer", "Tanjiro",
            "My Hero Academia", "Deku", "All Might", "Jujutsu Kaisen", "Gojo", "Sukuna",
            "PQ", "Pika", "Pokémon", "Ash Ketchum", "Pikachu",
            "Marvel", "DC", "Superman", "Batman", "Spider-Man", "Iron Man",
            "Star Wars", "Luke Skywalker", "Darth Vader", "Yoda",
            "Harry Potter", "Hermione", "Ron", "Hogwarts",
            "Disney", "Mickey Mouse", "Donald Duck", "Frozen", "Elsa",
            "Mario", "Luigi", "Zelda", "Link", "Pokémon", "Sonic",
            "Fortnite", "Minecraft", "Among Us", "Roblox",
            "Anime", "Manga"
        ]
        
        # Check if any copyrighted terms are in the prompt
        prompt_lower = prompt.lower()
        has_copyrighted = any(term.lower() in prompt_lower for term in copyrighted_terms)
        
        if not has_copyrighted and not key_elements:
            # No obvious copyrighted content, return original
            return prompt
        
        # Build system prompt
        system_prompt = """You are a helpful assistant that rephrases image generation prompts to avoid copyrighted, trademarked, or protected content. 
Your task is to take a user's prompt and rewrite it using ONLY generic, non-copyrighted descriptions while preserving the visual essence, mood, and composition.

CRITICAL RULES:
1. NEVER use any character names from anime, comics, movies, games, or TV shows
2. NEVER use any brand names, product names, or trademarks
3. NEVER use any franchise names (Marvel, DC, Disney, Nintendo, etc.)
4. Replace copyrighted characters with generic descriptions (e.g., "a pirate with a straw hat" instead of "Luffy")
5. Replace copyrighted locations with generic equivalents (e.g., "a Mediterranean city" instead of "Nice" if problematic, or "a tropical island" instead of specific locations)
6. Replace copyrighted objects with generic equivalents
7. Preserve the overall scene, action, and atmosphere
8. Keep the rephrased prompt in the same language as the original
9. If the original is in French, respond in French
10. Return ONLY the rephrased prompt, nothing else
11. Make it natural and readable
12. If you cannot avoid copyrighted content, make it more generic

Examples:
- "Luffy walking in Nice" -> "A young adventurer with a straw hat walking in a Mediterranean coastal city"
- "A man listening to rap" -> "A man listening to music with headphones"
- "Pikachu eating pizza" -> "A small yellow electric rodent eating a slice of pizza"
- "Spider-Man swinging" -> "A superhero in a red and blue costume swinging between buildings"

Remember: Be creative but NEVER use copyrighted content."""

        user_prompt = f"""Please rephrase this image generation prompt to avoid all copyrighted/trademarked content:

Original prompt: {prompt}

Rephrased prompt (generic, non-copyrighted):"""

        try:
            api_key = config.MISTRAL_API_KEY
            if not api_key:
                # Fallback: simple manual replacement
                return BlackforestImageGenerator._simple_rephrase(prompt, copyrighted_terms)

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
                "temperature": 0.3,  # More deterministic for rephrasing
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
                    rephrased = data["choices"][0]["message"]["content"].strip()
                    rephrased = rephrased.strip('"\'\n')
                    print(f"[DEBUG] Mistral rephrased: '{prompt[:50]}...' -> '{rephrased[:50]}...'")
                    return rephrased
                else:
                    print(f"Mistral rephrase API error: {response.status_code} - {response.text}")
                    # Fallback to simple rephrase
                    return BlackforestImageGenerator._simple_rephrase(prompt, copyrighted_terms)

        except Exception as e:
            print(f"Error rephrasing with Mistral: {str(e)}")
            # Fallback to simple rephrase
            return BlackforestImageGenerator._simple_rephrase(prompt, copyrighted_terms)

    @staticmethod
    def _simple_rephrase(prompt: str, copyrighted_terms: list[str]) -> str:
        """Simple fallback rephrasing without Mistral API."""
        import re
        result = prompt
        
        # Simple replacements
        replacements = {
            "Luffy": "a young adventurer with a straw hat",
            "Monkey D. Luffy": "a straw-hatted adventurer",
            "PQ": "music",
            "Pokémon": "creatures",
            "Pikachu": "a small yellow electric creature",
            "Nice": "a Mediterranean city",
            "One Piece": "an adventure",
            "rap": "music",
            "album": "music",
        }
        
        for original, replacement in replacements.items():
            result = re.sub(re.escape(original), replacement, result, flags=re.IGNORECASE)
        
        return result

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


async def _generate_local_placeholder(
    prompt: str,
    output_path: str,
    width: int = 1024,
    height: int = 1024,
) -> str:
    """Create a local placeholder image (offline / local mode).

    Uses Pillow to draw the prompt text on a pastel background so the
    app works end-to-end without any external image-generation API.
    """
    from PIL import Image, ImageDraw, ImageFont

    # Deterministic pastel background color from the prompt
    import hashlib

    digest = hashlib.md5(prompt.encode("utf-8")).digest()
    bg = tuple(120 + (digest[i] % 100) for i in range(3))

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except OSError:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except OSError:
            try:
                font = ImageFont.load_default(size=32)
            except TypeError:
                font = ImageFont.load_default()

    try:
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    except OSError:
        try:
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
        except OSError:
            small_font = font

    # "LOCAL MODE" badge at the top
    badge = "LOCAL MODE - OFFLINE IMAGE"
    draw.text((24, 24), badge, fill="white", font=small_font)

    # Word-wrap the prompt and center it
    max_width = width - 80
    lines: list[str] = []
    current = ""
    for word in prompt.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    line_height = 44
    block_height = len(lines) * line_height
    y = (height - block_height) // 2
    for line in lines:
        line_width = draw.textlength(line, font=font)
        x = (width - line_width) // 2
        draw.text((x, y), line, fill="white", font=font)
        y += line_height

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    print(f"[local-mode] Saved placeholder image to {output_path}")
    return output_path


async def get_blackforest_generator(api_key: str, base_url: str = None) -> BlackforestImageGenerator:
    """
    Get or create the global Blackforest image generator instance.
    
    Args:
        api_key: Blackforest API key
        base_url: Optional base URL override (defaults to config.BFL_BASE_URL or api.bfl.ai)
        
    Returns:
        BlackforestImageGenerator instance
    """
    global _blackforest_generator
    if _blackforest_generator is None:
        # Use provided base_url, or fall back to config, or default
        effective_base_url = base_url or config.BFL_BASE_URL
        print(f"[DEBUG] get_blackforest_generator: config.BFL_BASE_URL={config.BFL_BASE_URL}, effective_base_url={effective_base_url}")
        _blackforest_generator = BlackforestImageGenerator(api_key=api_key, base_url=effective_base_url)
    else:
        print(f"[DEBUG] get_blackforest_generator: using cached generator with base_url={_blackforest_generator.base_url}")
    return _blackforest_generator


async def generate_image_from_prompt(
    prompt: str,
    output_path: str,
    width: int = 1024,
    height: int = 1024,
    model: str = None,
    use_mistral_enhancement: bool = False,
    key_elements: list[str] | None = None,
    timeout: float = 20.0,
    auto_rephrase: bool = True
) -> str:
    """
    Generate an image from a text prompt using Blackforest FLUX API.
    
    This is a convenience function that uses the global image generator.
    
    Args:
        prompt: The text prompt to generate an image from
        output_path: Path where the generated image will be saved
        width: Width of the generated image in pixels
        height: Height of the generated image in pixels
        model: Blackforest model identifier (default: flux-2-pro)
        use_mistral_enhancement: Whether to enhance the prompt using Mistral LLM (default: False)
        key_elements: List of 3-5 important words/objects that MUST appear prominently
        timeout: Maximum time to wait for image generation in seconds (default: 20)
        auto_rephrase: Whether to automatically rephrase prompts that trigger moderation errors (default: True)
        
    Returns:
        The output path where the image was saved
    """
    if config.LOCAL_MODE:
        return await _generate_local_placeholder(prompt, output_path, width, height)

    generator = await get_blackforest_generator(config.BFL_API_KEY)
    return await generator.generate_image(
        prompt,
        output_path,
        width=width,
        height=height,
        model=model,
        use_mistral_enhancement=use_mistral_enhancement,
        key_elements=key_elements,
        timeout=timeout,
        auto_rephrase=auto_rephrase
    )
