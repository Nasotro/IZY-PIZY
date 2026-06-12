#!/usr/bin/env python3
"""
Complete integration test for Blackforest image generation flow.
Tests the full story image generation pipeline.

Usage:
    python test_complete_blackforest_flow.py
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import config
from models.blackforest_image_generation import generate_image_from_prompt


async def test_complete_flow():
    """Test the complete image generation flow."""
    print("=" * 60)
    print("Complete Blackforest Flow Test")
    print("=" * 60)
    
    # Verify config
    print(f"\nConfiguration:")
    print(f"  BFL_API_KEY: {'***' + config.BFL_API_KEY[-4:] if config.BFL_API_KEY else 'NOT SET'}")
    print(f"  IMAGE_STORAGE_DIR: {config.IMAGE_STORAGE_DIR}")
    
    if not config.BFL_API_KEY:
        print("\n[FAIL] BFL_API_KEY is not configured")
        return False
    
    # Test 1: Generate image with default settings
    print("\n[Test 1] Generating image with default settings...")
    try:
        prompt = "A peaceful forest scene with sunlight filtering through trees"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = config.IMAGE_STORAGE_DIR / f"test_flow_{timestamp}.png"
        
        # Ensure directory exists
        config.IMAGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        
        result = await generate_image_from_prompt(
            prompt=prompt,
            output_path=str(output_path)
        )
        
        if Path(result).exists():
            size = Path(result).stat().st_size
            print(f"  [PASS] Image created: {result} ({size:,} bytes)")
        else:
            print(f"  [FAIL] Image not found at {result}")
            return False
    except Exception as e:
        print(f"  [FAIL] {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Generate image with custom dimensions
    print("\n[Test 2] Generating image with custom dimensions...")
    try:
        prompt = "A futuristic cityscape at night"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = config.IMAGE_STORAGE_DIR / f"test_custom_{timestamp}.png"
        
        result = await generate_image_from_prompt(
            prompt=prompt,
            output_path=str(output_path),
            width=768,
            height=1024
        )
        
        if Path(result).exists():
            size = Path(result).stat().st_size
            print(f"  [PASS] Custom size image created: {result} ({size:,} bytes)")
        else:
            print(f"  [FAIL] Image not found at {result}")
            return False
    except Exception as e:
        print(f"  [FAIL] {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Generate image without Mistral enhancement
    print("\n[Test 3] Generating image without Mistral enhancement...")
    try:
        prompt = "A simple red apple on a white table"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = config.IMAGE_STORAGE_DIR / f"test_no_enhance_{timestamp}.png"
        
        result = await generate_image_from_prompt(
            prompt=prompt,
            output_path=str(output_path),
            use_mistral_enhancement=False
        )
        
        if Path(result).exists():
            size = Path(result).stat().st_size
            print(f"  [PASS] Image without enhancement created: {result} ({size:,} bytes)")
        else:
            print(f"  [FAIL] Image not found at {result}")
            return False
    except Exception as e:
        print(f"  [FAIL] {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Generate image with specific model
    print("\n[Test 4] Generating image with specific model...")
    try:
        prompt = "A cute robot character"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = config.IMAGE_STORAGE_DIR / f"test_model_{timestamp}.png"
        
        result = await generate_image_from_prompt(
            prompt=prompt,
            output_path=str(output_path),
            model="flux-2-pro"
        )
        
        if Path(result).exists():
            size = Path(result).stat().st_size
            print(f"  [PASS] Image with specific model created: {result} ({size:,} bytes)")
        else:
            print(f"  [FAIL] Image not found at {result}")
            return False
    except Exception as e:
        print(f"  [FAIL] {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("All flow tests completed successfully!")
    print("=" * 60)
    return True


async def test_error_handling():
    """Test error handling scenarios."""
    print("\n" + "=" * 60)
    print("Error Handling Tests")
    print("=" * 60)
    
    # Test 1: Invalid API key
    print("\n[Test 1] Testing with invalid API key...")
    try:
        from models.blackforest_image_generation import BlackforestImageGenerator
        
        generator = BlackforestImageGenerator(api_key="invalid_key_12345")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = config.IMAGE_STORAGE_DIR / f"test_invalid_{timestamp}.png"
        
        try:
            await generator.generate_image(
                prompt="test",
                output_path=str(output_path),
                width=512,
                height=512
            )
            print("  [FAIL] Should have raised an error with invalid API key")
            return False
        except RuntimeError as e:
            print(f"  [PASS] Correctly raised error: {str(e)[:50]}...")
    except Exception as e:
        print(f"  [FAIL] Unexpected error: {str(e)}")
        return False
    
    print("\n" + "=" * 60)
    print("Error handling tests completed!")
    print("=" * 60)
    return True


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("COMPLETE BLACKFOREST INTEGRATION TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Run complete flow tests
    results.append(("Complete Flow", await test_complete_flow()))
    
    # Run error handling tests
    results.append(("Error Handling", await test_error_handling()))
    
    # Summary
    print("\n" + "=" * 60)
    print("FINAL TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n[SUCCESS] All integration tests passed!")
        print("\nThe Blackforest image generation is ready to use!")
        print("\nTo use it:")
        print("1. Set your BFL_API_KEY in .env file")
        print("2. Run the backend server")
        print("3. Call POST /api/stories/{story_id}/generate-image")
        return 0
    else:
        print("\n[FAILURE] Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
