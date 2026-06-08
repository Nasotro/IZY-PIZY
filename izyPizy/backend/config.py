from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "../data/izypizy.db")
PI_FILE: str = os.getenv("PI_FILE", "../data/pi.txt")
IMAGE_STORAGE_DIR: Path = Path(os.getenv("IMAGE_STORAGE_DIR", "../data/images"))
RUNWARE_API_KEY: str = os.getenv("RUNWARE_API_KEY", "")
MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")

if not RUNWARE_API_KEY:
    raise ValueError("RUNWARE_API_KEY is not configured in environment variables")
