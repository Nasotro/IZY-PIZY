# Image Generation Refactoring - Runware SDK

## Summary

Successfully refactored the image generation module from Google GenAI to Runware SDK.

## Changes Made

### 1. Backend - `routers/stories.py`
**Fixed the image path storage issue:**
- **Before**: `relative_path = f"images/{image_filename}"` - This caused URLs like `/api/images/images/filename.png`
- **After**: `relative_path = image_filename` - Now URLs are correctly `/api/images/filename.png`
- **Comment updated**: Changed "Generate image using Google GenAI" to "Generate image using Runware"

### 2. Existing Files (Already in place from previous work)
- `models/image_generation.py` - Complete Runware implementation with `ImageGenerator` class
- `config.py` - Has `RUNWARE_API_KEY` configuration
- `requirements.txt` - Has `runware` and `aiohttp` dependencies
- `routers/images.py` - Static file serving for images
- `frontend/src/lib/api.js` - Has `getImageUrl()` function
- `frontend/src/components/StoryCard.svelte` - Button logic is correct

## How It Works

### Image Generation Flow

1. **Frontend** calls `POST /api/stories/{story_id}/generate-image`
2. **Backend** (`routers/stories.py`):
   - Validates the story exists and has a sentence
   - Checks RUNWARE_API_KEY is configured
   - Generates filename: `story_{story_id}_{uuid}.png`
   - Saves to `IMAGE_STORAGE_DIR` (default: `../data/images`)
   - Stores just the filename in database (e.g., `story_123_abc123.png`)
3. **Frontend** receives updated story with `image_path` set
4. **Frontend** displays image using `getImageUrl(image_path)` = `/api/images/{image_path}`
5. **Images Router** (`routers/images.py`):
   - Mounts `IMAGE_STORAGE_DIR` at `/api/images`
   - Serves the file directly

### Button Display Logic

In `StoryCard.svelte`:
```javascript
// Button is shown when:
canGenerateImage = !!story.sentence  // Story has a sentence
!imageSrc = !story.image_path        // No image yet

// Button is disabled when:
generatingImage = true  // Image generation in progress
```

## Testing

All tests pass:

1. **Basic Runware connection** - ✓ PASSED
2. **Direct SDK usage** - ✓ PASSED  
3. **Full image generation** - ✓ PASSED
4. **Path format validation** - ✓ PASSED
5. **Image serving compatibility** - ✓ PASSED

### Test Scripts

Run the tests:
```bash
# Test Runware SDK functionality
python test_runware_image_generation.py

# Test complete flow including path handling
python test_complete_image_flow.py
```

## API Key

The Runware API key is configured in `.env`:
```
RUNWARE_API_KEY=2WqZNAhSjKVaJgNcfjworImQEDW08OwO
```

## Dependencies

Install required packages:
```bash
pip install runware aiohttp
```

Remove old Google GenAI if present:
```bash
pip uninstall google-genai
```

## Image Path Migration

If you have existing stories with images stored with the old path format (`images/filename.png`), you'll need to:

1. Update the database to remove the `images/` prefix from all `image_path` values
2. Or update the images router to handle both formats

Currently there are no existing images in the database, so no migration is needed.

## Model Configuration

The image generation uses:
- **Model**: `runware:101@1` (default)
- **Dimensions**: 1024x1024 (default)
- **Provider**: Runware SDK

These can be customized by passing different parameters to `generate_image_from_prompt()`.
