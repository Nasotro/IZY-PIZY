#!/usr/bin/env python3
"""
Test script to verify image serving works for both old and new path formats.
"""
import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import config
from routers.images import router
from fastapi.testclient import TestClient
from main import app


async def test_image_serving():
    """Test image serving for both old and new path formats."""
    print("\n" + "=" * 60)
    print("Testing Image Serving (Old and New Path Formats)")
    print("=" * 60)
    
    # Ensure image directory exists
    config.IMAGE_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create test images
    test_image_old = config.IMAGE_STORAGE_DIR / "story_4_test.png"
    test_image_new = config.IMAGE_STORAGE_DIR / "story_6_test.png"
    
    # Create dummy image files
    dummy_image = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"  # Minimal PNG header
    test_image_old.write_bytes(dummy_image)
    test_image_new.write_bytes(dummy_image)
    
    print(f"\nCreated test images:")
    print(f"  {test_image_old.name}")
    print(f"  {test_image_new.name}")
    
    # Test with FastAPI TestClient
    client = TestClient(app)
    
    # Test 1: New format (no 'images/' prefix)
    print("\n[Test 1] New format: /api/images/story_6_test.png")
    response = client.get("/api/images/story_6_test.png")
    if response.status_code == 200:
        print(f"  {response.status_code} OK - Image served successfully")
    else:
        print(f"  {response.status_code} FAILED - {response.text}")
        return False
    
    # Test 2: Old format (with 'images/' prefix)
    print("\n[Test 2] Old format: /api/images/images/story_4_test.png")
    response = client.get("/api/images/images/story_4_test.png")
    if response.status_code == 200:
        print(f"  {response.status_code} OK - Image served successfully (backwards compatible)")
    else:
        print(f"  {response.status_code} FAILED - {response.text}")
        return False
    
    # Test 3: Non-existent image
    print("\n[Test 3] Non-existent image: /api/images/nonexistent.png")
    response = client.get("/api/images/nonexistent.png")
    if response.status_code == 404:
        print(f"  {response.status_code} OK - Correctly returns 404")
    else:
        print(f"  {response.status_code} FAILED - Expected 404")
        return False
    
    # Clean up test files
    test_image_old.unlink(missing_ok=True)
    test_image_new.unlink(missing_ok=True)
    
    print("\n" + "=" * 60)
    print("All image serving tests passed!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    result = asyncio.run(test_image_serving())
    sys.exit(0 if result else 1)
