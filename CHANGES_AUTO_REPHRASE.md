# Automatic Prompt Rephrasing for Moderation Errors

## Summary

This update adds automatic prompt rephrasing using Mistral API when Blackforest image generation returns moderation errors due to copyrighted/trademarked content. This addresses the issue where prompts containing terms like "Luffy", "PQ", "Pokémon", etc. are blocked by Blackforest's content moderation.

## Problem

The debug output from the API showed:
```
[DEBUG] Model flux-2-pro: POLL response status=200, status_field=Request Moderated, text={"id":"...","status":"Request Moderated","result":null,"progress":null,"details":{"Moderation Reasons":["Protected Content"]},...}
```

This meant that prompts with copyrighted content were being rejected, causing all models to fail.

## Solution

The system now:
1. Detects moderation errors ("Request Moderated", "Protected Content", "copyright", "trademark")
2. Automatically uses Mistral API to rephrase the prompt to avoid copyrighted content
3. Retries image generation with the rephrased prompt
4. Falls back to simple string replacement if Mistral API is unavailable

## Files Modified

### Backend

#### 1. `backend/models/blackforest_image_generation.py`

**New Method:** `rephrase_to_avoid_copyright(prompt, key_elements)`
- Uses Mistral LLM to intelligently rephrase prompts
- Avoids copyrighted characters, brands, franchises
- Preserves the visual essence and mood of the original
- Falls back to `_simple_rephrase()` if Mistral API fails

**New Method:** `_simple_rephrase(prompt, copyrighted_terms)`
- Fallback rephrasing without Mistral API
- Uses simple string replacements for known copyrighted terms

**Updated Method:** `generate_image()`
- Added `auto_rephrase` parameter (default: True)
- Tracks tried prompts to avoid infinite loops
- Detects moderation errors in exceptions
- Automatically retries with rephrased prompt when moderation is detected
- Maintains all existing functionality (auto_fallback, model discovery, etc.)

**Updated Function:** `generate_image_from_prompt()`
- Added `auto_rephrase` parameter
- Passes it through to `generate_image()`

#### 2. `backend/models/stories.py`

**Updated Class:** `ImageGenerationOptions`
- Added `auto_rephrase: bool = True` field

#### 3. `backend/routers/stories.py`

**Updated Endpoint:** `POST /stories/{story_id}/generate-image`
- Added `auto_rephrase` query parameter (default: True)
- Passes parameter to `generate_image_from_prompt()`

**Updated Endpoint:** `POST /stories/{story_id}/generate-image-batch`
- Extracts `auto_rephrase` from options (default: True)
- Passes parameter to `generate_image_from_prompt()`

### Frontend

#### 4. `frontend/src/components/ImageGenerationModal.svelte`

**New State Variable:**
- `autoRephrase = true` - Toggle state for auto-rephrase feature

**New UI Element:**
- Added toggle switch for "Auto Fix Copyright Issues"
- Description: "Automatically rephrase prompts that trigger moderation errors"

**Updated Function:** `handleGenerate()`
- Passes `auto_rephrase: autoRephrase` in the options object

## How It Works

### Flow Diagram

```
User Request
    ↓
Generate Image with Prompt
    ↓
[If moderation error?]
    ↓ YES
Rephrase Prompt with Mistral
    ↓
Retry with New Prompt
    ↓
[Success?]
    ↓ YES
Return Image
    ↓ NO
[More models to try?]
    ↓ YES
Try Next Model
    ↓ NO
[Max retries exceeded?]
    ↓ YES
Return Error
```

### Example Transformation

**Input:** `"Il croise Luffy à Nice qui marche sur du PQ, et qui écoute un album de rap rare."`

**Mistral Rephrases To:** `"A young adventurer with a straw hat walking in a Mediterranean city listening to music with headphones"`

**Result:** Image generation succeeds because the prompt no longer contains copyrighted terms.

## Configuration

### Backend (Python)

```python
# Default behavior - auto-rephrase enabled
await generate_image_from_prompt(
    prompt,
    output_path,
    auto_rephrase=True  # Default
)

# Disable auto-rephrase
await generate_image_from_prompt(
    prompt,
    output_path,
    auto_rephrase=False
)
```

### Frontend (Svelte)

The toggle is enabled by default in the ImageGenerationModal component.

### API Endpoint

```bash
# Generate with auto-rephrase enabled (default)
POST /api/stories/9/generate-image-batch
{
  "num_images": 3,
  "custom_prompt": "Luffy in Nice",
  "auto_rephrase": true
}

# Disable auto-rephrase
POST /api/stories/9/generate-image-batch
{
  "num_images": 3,
  "custom_prompt": "Luffy in Nice",
  "auto_rephrase": false
}
```

## Known Copyrighted Terms Handled

The system recognizes and avoids:
- Anime/Manga: Luffy, Naruto, Goku, Spider-Man, etc.
- Games: Pokémon, PQ, Mario, Zelda, Fortnite, Minecraft
- Franchises: Disney, Marvel, DC, Star Wars, Harry Potter
- Music: Specific album names, artist names
- Brands: Product names, trademarks

## Testing

Run the test script to verify functionality:

```bash
python test_auto_rephrase.py
```

This tests:
1. Direct rephrasing of copyrighted prompts
2. Moderation error detection
3. Simple fallback rephrasing

## Benefits

1. **Automatic Recovery**: No manual intervention needed when moderation errors occur
2. **Preserves Intent**: Rephrased prompts maintain the visual scene and mood
3. **Graceful Degradation**: Falls back to simple replacement if Mistral is unavailable
4. **User Control**: Can be disabled via parameter if desired
5. **Transparent**: Debug logs show when rephrasing occurs

## Debug Output

When auto-rephrase is triggered, you'll see:

```
[DEBUG] Moderation error detected, rephrasing prompt: 'Luffy walking in Nice...'
[DEBUG] Mistral rephrased: 'Luffy walking in Nice...' -> 'A young adventurer with a straw hat walking in a Mediterranean city...'
[DEBUG] Retrying with rephrased prompt: 'A young adventurer with a straw hat walking in a Mediterranean city...'
```

## Notes

- The feature is **enabled by default** in both backend and frontend
- Requires Mistral API key to be configured in `.env` for best results
- Works without Mistral API using simple string replacement (less effective)
- Only triggers when moderation errors are detected
- Does not affect prompts without copyrighted content
