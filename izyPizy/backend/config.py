from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "../data/izypizy.db")
PI_FILE: str = os.getenv("PI_FILE", "../data/pi.txt")
GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
IMAGE_STORAGE_DIR: Path = Path(os.getenv("IMAGE_STORAGE_DIR", "../data/images"))

print(f"Using GOOGLE_API_KEY: {GOOGLE_API_KEY[:5]}...{GOOGLE_API_KEY[-5:]}")
