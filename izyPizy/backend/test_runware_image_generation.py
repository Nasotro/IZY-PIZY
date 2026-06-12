#!/usr/bin/env python3
"""
Test script for Runware image generation.
Tests the new image_generation.py module.

Usage:
    python test_runware_image_generation.py

This script will:
1. Load the RUNWARE_API_KEY from .env
2. Test the Runware connection
3. Generate a test image
4. Save it to the images directory
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime

# Add the backend directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import our image generation module
from models.image_generation import ImageGenerator, generate_image_from_prompt
import config


async def test_runware_connection():
    """Test that we can connect to Runware API."""
    print("Testing Runware connection...")
    
    api_key = config.RUNWARE_API_KEY
    if not api_key:
        print("ERROR: RUNWARE_API_KEY not found in environment")
        return False
    
    print(f"API Key loaded: {api_key[:10]}...")
    
    generator = ImageGenerator(api_key=api_key)
    
    try:
        await generator.connect()
        print("[PASS] Successfully connected to Runware API")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to connect to Runware: {str(e)}")
        return False


async def test_image_generation():
    """Test generating an actual image."""
    print("\nTesting image generation...")
    
    # Create test prompt
    prompt = "A beautiful sunset over mountains, digital art style"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = config.IMAGE_STORAGE_DIR / f"test_runware_{timestamp}.png"
    
    # Ensure image directory exists
    config.IMAGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Prompt: '{prompt}'")
    print(f"Output path: {output_path}")
    
    try:
        # Use the convenience function
        result_path = await generate_image_from_prompt(
            prompt=prompt,
            output_path=str(output_path),
            width=1024,
            height=1024
        )
        
        # Check if file was created
        if Path(result_path).exists():
            file_size = Path(result_path).stat().st_size
            print(f"[PASS] Image generated successfully!")
            print(f"  File: {result_path}")
            print(f"  Size: {file_size:,} bytes")
            return True
        else:
            print(f"[FAIL] Image file not found at {result_path}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Failed to generate image: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_direct_sdk_usage():
    """Test direct usage of Runware SDK (similar to the snippet provided)."""
    print("\nTesting direct Runware SDK usage...")
    
    try:
        from runware import Runware, IImageInference
        
        runware = Runware(api_key=config.RUNWARE_API_KEY)
        await runware.connect()
        
        request = IImageInference(
            positivePrompt="A serene mountain landscape at sunset",
            model="runware:101@1",
            width=1024,
            height=1024
        )
        
        images = await runware.imageInference(requestImage=request)
        
        if images and images[0].imageURL:
            print(f"[PASS] Direct SDK call successful!")
            print(f"  Image URL: {images[0].imageURL}")
            return True
        else:
            print("[FAIL] No image URL returned from Runware")
            return False
            
    except Exception as e:
        print(f"[FAIL] Direct SDK test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Runware Image Generation Test Script")
    print("=" * 60)
    
    # Verify config
    print(f"\nConfiguration:")
    print(f"  RUNWARE_API_KEY: {'***' + config.RUNWARE_API_KEY[-4:] if config.RUNWARE_API_KEY else 'NOT SET'}")
    print(f"  IMAGE_STORAGE_DIR: {config.IMAGE_STORAGE_DIR}")
    
    results = []
    
    # Test 1: Connection
    results.append(("Runware Connection", await test_runware_connection()))
    
    # Test 2: Direct SDK usage
    results.append(("Direct SDK Usage", await test_direct_sdk_usage()))
    
    # Test 3: Full image generation
    results.append(("Image Generation", await test_image_generation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[FAILURE] Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
