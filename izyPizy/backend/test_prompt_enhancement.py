#!/usr/bin/env python3
"""
Test script for Mistral prompt enhancement functionality.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from models.image_generation import ImageGenerator


async def test_prompt_enhancement():
    """Test that prompts are enhanced correctly using Mistral."""
    print("\n" + "=" * 60)
    print("Testing Mistral Prompt Enhancement")
    print("=" * 60)
    
    generator = ImageGenerator(api_key="test")
    
    test_cases = [
        "A cat on a roof",
        "A princess in a castle",
        "The moon over the ocean",
        "A dragon flying in the sky",
        "Two friends sharing a secret",
    ]
    
    for i, sentence in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Original: '{sentence}'")
        enhanced = await generator.enhance_prompt_with_mistral(sentence)
        print(f"Enhanced: '{enhanced[:100]}...'" if len(enhanced) > 100 else f"Enhanced: '{enhanced}'")
        
        # Basic validation
        if enhanced == sentence:
            print("  Note: Enhancement returned original (API may have failed or no key)")
        elif len(enhanced) > len(sentence):
            print("  [PASS] Prompt was enhanced")
        else:
            print("  [WARN] Enhanced prompt is shorter than original")
    
    print("\n" + "=" * 60)
    print("Prompt enhancement test completed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_prompt_enhancement())
