from fastapi import APIRouter, Response
from fastapi.staticfiles import StaticFiles
import config
from pathlib import Path

router = APIRouter()

# Custom route to handle image requests
# This handles both old format (images/filename.png) and new format (filename.png)
@router.get("/images/{image_path:path}")
async def serve_image(image_path: str):
    """
    Serve an image file.
    
    Handles both old path format (images/filename.png) and new format (filename.png).
    For backwards compatibility, if the path starts with 'images/', we strip it.
    """
    # Remove 'images/' prefix if present (for backwards compatibility)
    if image_path.startswith("images/"):
        actual_path = image_path[7:]  # Remove the first 7 characters "images/"
    else:
        actual_path = image_path
    
    file_path = config.IMAGE_STORAGE_DIR / actual_path
    
    if not file_path.exists():
        return Response(status_code=404, content="Image not found")
    
    return Response(content=file_path.read_bytes(), media_type="image/png")
