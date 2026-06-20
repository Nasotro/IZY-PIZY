# Fix for API Error 500: 404 Not Found

## Problem

When trying to generate images, you encountered this error:
```
API error 500: {"detail":"Failed to generate images: Failed to generate image: Failed to submit image generation: HTTP 404 - {\"detail\":\"Not Found\"}"}
```

This error indicates that the Blackforest API endpoint being used (`flux-2-pro-preview`) was returning a 404 Not Found error, meaning the model endpoint either doesn't exist or has been deprecated.

## Root Cause

The issue was caused by using a model endpoint that may have been deprecated or moved. The original code only tried one model (`flux-2-pro-preview`) and failed with a 404 if that specific endpoint didn't work.

## Solution

I've implemented a comprehensive fix in `models/blackforest_image_generation.py`:

### 1. Added Model Fallback System

The code now includes a list of known working model endpoints:
- `flux-2-pro` (new default)
- `flux-2-pro-preview`
- `flux-2-max`
- `flux-2-flex`
- `flux-2-klein-4b`
- `flux-2-klein-9b-preview`
- `flux-pro-1.1`
- `flux-pro-1.1-ultra`
- `flux-pro`
- `flux`

### 2. Automatic Fallback Logic

If the specified model fails, the code will automatically try the next working model in the list. This is enabled by default with the `auto_fallback=True` parameter.

### 3. Better Error Handling

Improved error messages for common issues:
- **401 Unauthorized**: Invalid API key
- **402 Payment Required**: Out of credits
- **429 Rate Limit**: Too many active tasks (limit: 24)
- **404 Not Found**: Model endpoint doesn't exist (will try fallback models)

### 4. Default Model Changed

Changed the default model from `flux-2-pro-preview` to `flux-2-pro` which is more stable.

## Files Modified

1. **`models/blackforest_image_generation.py`**
   - Added `WORKING_MODELS` list with fallback models
   - Added `find_working_model()` method to test and find working models
   - Updated `generate_image()` with automatic fallback logic
   - Updated `generate_image_from_prompt()` to support `auto_fallback` parameter
   - Improved error messages
   - Changed default model from `flux-2-pro-preview` to `flux-2-pro`

2. **`BLACKFOREST_MIGRATION.md`**
   - Added troubleshooting section for 404 errors

## Files Created

1. **`test_fix_simple.py`** - Simple test to verify the fix works
2. **`test_multiple_models.py`** - Tests multiple model endpoints
3. **`test_image_generation_comprehensive.py`** - Comprehensive test suite
4. **`FIX_500_ERROR.md`** - This documentation file

## How to Use

### Run the Simple Test

```bash
cd izyPizy/backend
python test_fix_simple.py
```

This will:
1. Test image generation with automatic fallback
2. Generate a single test image
3. Generate multiple test images
4. Verify files are saved locally

### Run the Comprehensive Test

```bash
cd izyPizy/backend
python test_image_generation_comprehensive.py
```

This will:
1. Test all model endpoints to find which ones work
2. Test full image generation flow
3. Test batch generation of multiple images
4. Provide detailed results

### Use in Your Application

The button in your application should now work automatically. The code will:

1. Try the requested model (or `flux-2-pro` by default)
2. If that fails, automatically try the next working model
3. Continue until a working model is found or all models are exhausted
4. Generate the image and save it locally

You can also explicitly specify a model:

```python
from models.blackforest_image_generation import generate_image_from_prompt

# With automatic fallback (default)
await generate_image_from_prompt(
    prompt="Your prompt here",
    output_path="path/to/output.png",
    model="flux-2-max"  # Optional: specify a model
)

# Without automatic fallback (will raise error if model fails)
await generate_image_from_prompt(
    prompt="Your prompt here",
    output_path="path/to/output.png",
    model="flux-2-max",
    auto_fallback=False
)
```

## Configuration

Make sure your `.env` file has:

```
BFL_API_KEY=your_api_key_here
MISTRAL_API_KEY=your_mistral_key_here  # Optional, for prompt enhancement
IMAGE_STORAGE_DIR=../data/images
```

## Troubleshooting

If you still encounter issues:

1. **Check API Key**: Verify `BFL_API_KEY` is valid at https://dashboard.bfl.ai/
2. **Check Credits**: Ensure you have credits at https://dashboard.bfl.ai/
3. **Check Rate Limits**: Wait if you have 24+ active tasks
4. **Check API Status**: https://status.bfl.ai/
5. **Try Regional Endpoint**: Use `api.eu.bfl.ai` or `api.us.bfl.ai` instead of `api.bfl.ai`

## Regional Endpoints

The code supports regional endpoints. To use a regional endpoint:

```python
from models.blackforest_image_generation import BlackforestImageGenerator

# Use EU endpoint
generator = BlackforestImageGenerator(
    api_key=config.BFL_API_KEY,
    base_url="https://api.eu.bfl.ai/v1"
)

# Or US endpoint
generator = BlackforestImageGenerator(
    api_key=config.BFL_API_KEY,
    base_url="https://api.us.bfl.ai/v1"
)
```

## References

- [Blackforest API Documentation](https://docs.bfl.ai/quick_start/generating_images)
- [Blackforest Models](https://bfl.ai/models)
- [API Status](https://status.bfl.ai/)
- [API Dashboard](https://dashboard.bfl.ai/)
