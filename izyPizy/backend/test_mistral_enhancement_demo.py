#!/usr/bin/env python3
"""
Demo script showing Mistral prompt enhancement for image generation.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from models.image_generation import ImageGenerator


async def demo_prompt_enhancement():
    """Demo the prompt enhancement functionality."""
    print("\n" + "=" * 70)
    print("MISTRAL PROMPT ENHANCEMENT DEMO")
    print("=" * 70)
    print("\nThis demonstrates how simple story sentences are transformed into")
    print("detailed, rich prompts for better AI image generation.\n")
    
    generator = ImageGenerator(api_key="test")
    
    test_cases = [
        "A cat on a roof",
        "A princess in a castle",
        "The moon over the ocean",
        "A dragon flying in the sky",
        "Two friends sharing a secret",
        "A magical forest at night",
        "A knight riding a horse",
        "A birthday party with cake",
    ]
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"\n[{i}] ORIGINAL STORY:")
        print(f"   '{sentence}'")
        
        enhanced = await generator.enhance_prompt_with_mistral(sentence)
        
        print(f"\n   ENHANCED PROMPT (for AI image generation):")
        print(f"   '{enhanced}'")
        print("-" * 70)
    
    print("\n" + "=" * 70)
    print("BENEFITS OF PROMPT ENHANCEMENT:")
    print("=" * 70)
    print("""
[+] More visual details (colors, textures, lighting)
[+] Better composition and perspective
[+] Style suggestions (digital art, cinematic, etc.)
[+] Richer atmosphere and mood
[+] More interesting and engaging images
[+] Better AI understanding of the scene
    """)
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_prompt_enhancement())
