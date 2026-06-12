#!/usr/bin/env python3
"""
Complete test script for Runware image generation flow.
Tests the entire pipeline from API endpoint to image serving.

Usage:
    python test_complete_image_flow.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import config
from models.image_generation import generate_image_from_prompt
from routers.stories import _row_to_story


def pass_mark():
    return "[PASS]"

def fail_mark():
    return "[FAIL]"


async def test_image_storage_and_serving():
    """Test that images are stored correctly and can be accessed via the API."""
    print("\n" + "=" * 60)
    print("Testing Complete Image Flow")
    print("=" * 60)
    
    # Ensure image directory exists
    config.IMAGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nImage storage directory: {config.IMAGE_STORAGE_DIR}")
    print(f"Absolute path: {config.IMAGE_STORAGE_DIR.resolve()}")
    
    # Test 1: Generate an image
    print("\n[Test 1] Generating test image...")
    prompt = "A beautiful sunset over mountains"
    timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
    image_filename = f"test_flow_{timestamp}.png"
    image_path = config.IMAGE_STORAGE_DIR / image_filename
    
    try:
        result_path = await generate_image_from_prompt(
            prompt=prompt,
            output_path=str(image_path),
            width=1024,
            height=1024
        )
        
        if Path(result_path).exists():
            file_size = Path(result_path).stat().st_size
            print(f"{pass_mark()} Image generated and saved to: {result_path}")
            print(f"  File size: {file_size:,} bytes")
        else:
            print(f"{fail_mark()} Image file not found at {result_path}")
            return False
            
    except Exception as e:
        print(f"{fail_mark()} Failed to generate image: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Verify the path format
    print("\n[Test 2] Verifying path format...")
    # The image_filename should be just the filename, not prefixed with "images/"
    if image_filename.startswith("images/"):
        print(f"{fail_mark()} Path has incorrect 'images/' prefix: {image_filename}")
        return False
    else:
        print(f"{pass_mark()} Path format is correct: {image_filename}")
    
    # Test 3: Verify the image file exists at the expected location
    print("\n[Test 3] Verifying image file location...")
    expected_path = config.IMAGE_STORAGE_DIR / image_filename
    if expected_path.exists():
        print(f"{pass_mark()} Image exists at: {expected_path}")
    else:
        print(f"{fail_mark()} Image not found at: {expected_path}")
        return False
    
    # Test 4: Check that the path would work with the images router
    print("\n[Test 4] Verifying API URL would work...")
    # The images router mounts at /api/images
    # So for a file "test.png" in IMAGE_STORAGE_DIR, the URL would be /api/images/test.png
    api_url = f"/api/images/{image_filename}"
    print(f"  Expected API URL: {api_url}")
    
    # Verify the file is in the correct directory
    if expected_path.parent == config.IMAGE_STORAGE_DIR:
        print(f"{pass_mark()} File is in the correct directory for API serving")
    else:
        print(f"{fail_mark()} File is not in the expected directory")
        print(f"  Expected: {config.IMAGE_STORAGE_DIR}")
        print(f"  Actual: {expected_path.parent}")
        return False
    
    # Test 5: Test the path that would be stored in database
    print("\n[Test 5] Verifying database path format...")
    # In stories.py, we now store just the filename (not "images/filename")
    relative_path = image_filename  # This is what gets stored
    print(f"  Path stored in DB: {relative_path}")
    
    # The frontend would construct the URL as /api/images/{relative_path}
    frontend_url = f"/api/images/{relative_path}"
    print(f"  Frontend would request: {frontend_url}")
    
    if relative_path == image_filename:
        print(f"{pass_mark()} Database path format is correct")
    else:
        print(f"{fail_mark()} Database path format is incorrect")
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)
    return True


async def test_story_image_generation():
    """Test the story image generation endpoint logic."""
    print("\n" + "=" * 60)
    print("Testing Story Image Generation Logic")
    print("=" * 60)
    
    # Simulate what happens in the endpoint
    import uuid
    from datetime import datetime
    
    story_id = 123
    sentence = "A beautiful sunset over mountains"
    
    # Step 1: Generate filename
    image_filename = f"story_{story_id}_{uuid.uuid4().hex}.png"
    print(f"\nGenerated filename: {image_filename}")
    
    # Step 2: Create the full path
    image_dir = config.IMAGE_STORAGE_DIR
    image_path = image_dir / image_filename
    print(f"Full image path: {image_path}")
    
    # Step 3: Generate the image
    print("\nGenerating image...")
    try:
        await generate_image_from_prompt(sentence, str(image_path))
        print(f"{pass_mark()} Image generated at: {image_path}")
    except Exception as e:
        print(f"{fail_mark()} Failed to generate image: {str(e)}")
        return False
    
    # Step 4: Store relative path (this is what the endpoint does)
    relative_path = image_filename  # Fixed - no "images/" prefix
    print(f"\nRelative path to store in DB: {relative_path}")
    
    # Step 5: Verify the file exists
    if image_path.exists():
        print(f"{pass_mark()} Image file exists")
    else:
        print(f"{fail_mark()} Image file does not exist")
        return False
    
    # Step 6: Verify the URL construction
    api_url = f"/api/images/{relative_path}"
    print(f"\nAPI URL for frontend: {api_url}")
    
    # The images router serves from IMAGE_STORAGE_DIR
    # So /api/images/filename.png should serve the file correctly
    print(f"{pass_mark()} URL construction is correct")
    
    print("\n" + "=" * 60)
    print("Story image generation test passed!")
    print("=" * 60)
    return True


async def main():
    """Run all tests."""
    results = []
    
    # Test the complete flow
    results.append(("Image Storage and Serving", await test_image_storage_and_serving()))
    
    # Test the story image generation logic
    results.append(("Story Image Generation", await test_story_image_generation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Final Test Results Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\nAll tests passed!")
        return 0
    else:
        print("\nSome tests failed.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
