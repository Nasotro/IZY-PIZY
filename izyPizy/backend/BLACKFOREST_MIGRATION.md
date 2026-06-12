# Blackforest API Migration Guide

## Overview
This document describes the migration from Runaware to Blackforest Labs FLUX API for image generation in the IZY PIZY v2 backend.

## Changes Made

### 1. New Module: `models/blackforest_image_generation.py`
- Created a new module that implements image generation using Blackforest Labs FLUX API
- Features:
  - Asynchronous HTTP requests to Blackforest API endpoints
  - Automatic polling for image generation results
  - Support for multiple FLUX models (flux-2-pro-preview, flux-2-pro, etc.)
  - Optional Mistral LLM prompt enhancement
  - Image download and local storage

### 2. Configuration: `config.py`
- Added `BFL_API_KEY` environment variable
- Updated validation to accept either `BFL_API_KEY` or `RUNWARE_API_KEY` for backward compatibility
- Removed strict requirement for `RUNWARE_API_KEY`

### 3. Models: `models/stories.py`
- Updated import to use `blackforest_image_generation` instead of `image_generation`
- The `generate_image_from_prompt` function now uses Blackforest API

### 4. Router: `routers/stories.py`
- Updated `/stories/{story_id}/generate-image` endpoint
- Changed API key check from `RUNWARE_API_KEY` to `BFL_API_KEY`
- Updated docstring to reference Blackforest FLUX API
- Fixed typo in delete route (was `//stories` now `/stories`)

### 5. Requirements: `requirements.txt`
- Removed `runware` dependency
- Kept `httpx` and `aiohttp` for async HTTP requests

### 6. Environment: `.env`
- Added `BFL_API_KEY=` placeholder
- Kept `RUNWARE_API_KEY` for backward compatibility

### 7. Tests
- Created `test_blackforest_image_generation.py` - Unit tests for the new module
- Created `test_complete_blackforest_flow.py` - Integration tests for the full pipeline

## Blackforest API Details

### API Endpoints
- **Base URL**: `https://api.bfl.ai/v1`
- **Models Available**:
  - `flux-2-pro-preview` (default, latest)
  - `flux-2-pro` (stable snapshot)
  - `flux-2-flex`
  - `flux-2-klein-4b`
  - `flux-2-klein-9b-preview`
  - `flux-2-klein-9b`
  - And more (see [Blackforest Docs](https://docs.bfl.ai/quick_start/generating_images))

### API Flow
1. **Submit Request**: POST to `https://api.bfl.ai/v1/{model}` with prompt, width, height
2. **Receive Response**: Get `polling_url` and `id`
3. **Poll for Results**: GET `polling_url` until status is "Ready"
4. **Download Image**: GET the `result.sample` URL to download the image

### Authentication
- Use `x-key` header with your API key
- Get API key from [Blackforest Dashboard](https://dashboard.bfl.ai/)

## Setup Instructions

### 1. Get Blackforest API Key
- Visit https://dashboard.bfl.ai/
- Sign up or log in
- Create a new API key
- Copy the key

### 2. Configure Environment
Edit `izyPizy/backend/.env`:
```
BFL_API_KEY=your_actual_api_key_here
```

### 3. Install Dependencies
```bash
cd izyPizy/backend
pip install -r requirements.txt
```

### 4. Run Tests
```bash
# Test Blackforest integration
python test_blackforest_image_generation.py

# Test complete flow
python test_complete_blackforest_flow.py
```

## Usage

### API Endpoint
```
POST /api/stories/{story_id}/generate-image
```

This endpoint will:
1. Get the story sentence from the database
2. Generate an image using Blackforest FLUX API
3. Save the image to `../data/images/`
4. Store the relative path in the database
5. Return the updated story object

### Direct Usage
```python
from models.blackforest_image_generation import generate_image_from_prompt

# Generate image with defaults
await generate_image_from_prompt(
    prompt="A beautiful landscape",
    output_path="path/to/output.png"
)

# Generate with custom settings
await generate_image_from_prompt(
    prompt="A beautiful landscape",
    output_path="path/to/output.png",
    width=768,
    height=1024,
    model="flux-2-pro",
    use_mistral_enhancement=True
)
```

## Backward Compatibility

The system maintains backward compatibility:
- If `BFL_API_KEY` is not set but `RUNWARE_API_KEY` is, the old Runaware module can still be used
- The old `models/image_generation.py` is kept but not used by default
- To switch back to Runaware, update the imports in `models/stories.py`

## Model Comparison

| Feature | Runaware | Blackforest FLUX |
|---------|----------|------------------|
| API Type | SDK | REST API |
| Async Support | Yes | Yes |
| Models | runware:101@1 | flux-2-pro-preview, flux-2-pro, etc. |
| Image Quality | Good | Excellent (FLUX.2) |
| Pricing | Commercial | Credit-based |
| Documentation | Limited | Comprehensive |

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Check that `BFL_API_KEY` is set correctly in `.env`
   - Verify the API key is valid at https://dashboard.bfl.ai/

2. **429 Rate Limit**
   - Blackforest has a limit of 24 active tasks
   - Wait for existing tasks to complete

3. **402 Payment Required**
   - You've run out of credits
   - Add credits at https://dashboard.bfl.ai/

4. **Timeout Errors**
   - Image generation can take 30-60 seconds
   - Increase timeout in `blackforest_image_generation.py` if needed

5. **Module Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`

## Files Modified/Created

### Modified
- `config.py`
- `models/stories.py`
- `routers/stories.py`
- `requirements.txt`
- `.env`

### Created
- `models/blackforest_image_generation.py`
- `test_blackforest_image_generation.py`
- `test_complete_blackforest_flow.py`

### Kept (for reference)
- `models/image_generation.py` (old Runaware implementation)
- `test_runware_image_generation.py` (old tests)

## Migration Checklist

- [ ] Get Blackforest API key from dashboard
- [ ] Add `BFL_API_KEY` to `.env`
- [ ] Run `pip install -r requirements.txt`
- [ ] Run tests to verify everything works
- [ ] Test the `/stories/{id}/generate-image` endpoint
- [ ] Monitor for any issues in production

## References

- [Blackforest API Documentation](https://docs.bfl.ai/quick_start/generating_images)
- [FLUX Models](https://bfl.ai/models)
- [API Dashboard](https://dashboard.bfl.ai/)
- [GitHub - FLUX Repo](https://github.com/black-forest-labs/flux)
