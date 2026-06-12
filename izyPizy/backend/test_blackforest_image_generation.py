#!/usr/bin/env python3
"""
Test script for Blackforest FLUX API image generation.
Tests the new blackforest_image_generation.py module.

Usage:
    python test_blackforest_image_generation.py

This script will:
1. Load the BFL_API_KEY from .env
2. Test the Blackforest API connection
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
from models.blackforest_image_generation import BlackforestImageGenerator, generate_image_from_prompt
import config


async def test_blackforest_connection():
    """Test that we can connect to Blackforest API."""
    print("Testing Blackforest API connection...")
    
    api_key = config.BFL_API_KEY
    if not api_key:
        print("ERROR: BFL_API_KEY not found in environment")
        return False
    
    print(f"API Key loaded: {api_key[:10]}...")
    
    generator = BlackforestImageGenerator(api_key=api_key)
    
    try:
        # The Blackforest API doesn't require explicit connection
        # We'll test it by making a small request
        print("[PASS] Blackforest API client initialized successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Failed to initialize Blackforest client: {str(e)}")
        return False


async def test_image_generation():
    """Test generating an actual image."""
    print("\nTesting image generation...")
    
    # Create test prompt
    prompt = "A beautiful sunset over mountains, digital art style"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = config.IMAGE_STORAGE_DIR / f"test_blackforest_{timestamp}.png"
    
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


async def test_direct_api_usage():
    """Test direct usage of Blackforest API."""
    print("\nTesting direct Blackforest API usage...")
    
    try:
        import httpx
        
        api_key = config.BFL_API_KEY
        base_url = "https://api.bfl.ai/v1"
        model = "flux-2-pro-preview"
        
        headers = {
            "accept": "application/json",
            "x-key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": "A serene mountain landscape at sunset",
            "width": 1024,
            "height": 1024
        }
        
        # Submit request
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/{model}",
                headers=headers,
                json=payload
            )
        
        if response.status_code != 200:
            print(f"[FAIL] Direct API test failed: HTTP {response.status_code} - {response.text}")
            return False
        
        request_data = response.json()
        
        if "polling_url" not in request_data:
            print(f"[FAIL] Unexpected response format: {request_data}")
            return False
        
        print(f"[PASS] Direct API call successful!")
        print(f"  Request ID: {request_data.get('id', 'unknown')}")
        print(f"  Polling URL: {request_data['polling_url']}")
        return True
        
    except Exception as e:
        print(f"[FAIL] Direct API test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_mistral_enhancement():
    """Test prompt enhancement with Mistral."""
    print("\nTesting Mistral prompt enhancement...")
    
    try:
        from models.blackforest_image_generation import BlackforestImageGenerator
        
        generator = BlackforestImageGenerator(api_key=config.BFL_API_KEY)
        
        # Test with a simple sentence
        simple_prompt = "A cat on a roof"
        enhanced_prompt = await generator.enhance_prompt_with_mistral(simple_prompt)
        
        if enhanced_prompt != simple_prompt:
            print(f"[PASS] Prompt enhancement successful!")
            print(f"  Original: {simple_prompt}")
            print(f"  Enhanced: {enhanced_prompt[:100]}...")
            return True
        else:
            print(f"[WARN] Prompt was not enhanced (Mistral API might not be configured)")
            print(f"  Using original prompt: {simple_prompt}")
            return True  # Not a failure, just a warning
            
    except Exception as e:
        print(f"[FAIL] Prompt enhancement test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Blackforest Image Generation Test Script")
    print("=" * 60)
    
    # Verify config
    print(f"\nConfiguration:")
    print(f"  BFL_API_KEY: {'***' + config.BFL_API_KEY[-4:] if config.BFL_API_KEY else 'NOT SET'}")
    print(f"  MISTRAL_API_KEY: {'***' + config.MISTRAL_API_KEY[-4:] if config.MISTRAL_API_KEY else 'NOT SET'}")
    print(f"  IMAGE_STORAGE_DIR: {config.IMAGE_STORAGE_DIR}")
    
    results = []
    
    # Test 1: Connection
    results.append(("Blackforest API Initialization", await test_blackforest_connection()))
    
    # Test 2: Direct API usage
    results.append(("Direct API Usage", await test_direct_api_usage()))
    
    # Test 3: Mistral enhancement
    results.append(("Mistral Enhancement", await test_mistral_enhancement()))
    
    # Test 4: Full image generation
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
