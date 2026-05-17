from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
import config

router = APIRouter()

# Mount the images directory as static files
# This allows direct access to images via /api/images/filename.png
router.mount("/images", StaticFiles(directory=config.IMAGE_STORAGE_DIR), name="images")
