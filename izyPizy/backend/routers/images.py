import mimetypes

from fastapi import APIRouter, Response

import config

router = APIRouter()


@router.get("/images/{image_path:path}")
async def serve_image(image_path: str):
    """Serve a generated image or video from the storage directory.

    Handles both the legacy path format (``images/filename.png``) and the flat
    one. The media type is derived from the extension: generated videos used to
    be served as ``image/png``, which browsers refuse to play.
    """
    if image_path.startswith("images/"):
        actual_path = image_path[7:]
    else:
        actual_path = image_path

    file_path = (config.IMAGE_STORAGE_DIR / actual_path).resolve()
    # Never serve outside the storage directory.
    if config.IMAGE_STORAGE_DIR not in file_path.parents or not file_path.is_file():
        return Response(status_code=404, content="Image not found")

    media_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    return Response(
        content=file_path.read_bytes(),
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )
