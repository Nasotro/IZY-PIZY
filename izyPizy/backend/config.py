from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from the directory where this config.py file is located
# This ensures it works regardless of the current working directory
config_dir = Path(__file__).parent
env_path = config_dir / '.env'
load_dotenv(env_path)

# Also try loading from the parent directory for backward compatibility
parent_env_path = config_dir.parent / '.env'
if not os.path.exists(env_path) and os.path.exists(parent_env_path):
    load_dotenv(parent_env_path)

# Debug output
print(f"[DEBUG] Loaded .env from: {env_path if os.path.exists(env_path) else parent_env_path if os.path.exists(parent_env_path) else 'neither (using system env)'}")

BASE_DIR: Path = Path(__file__).parent
DATABASE_URL: str = os.getenv("DATABASE_URL", str(BASE_DIR / ".." / "data" / "izypizy.db"))
PI_FILE: str = os.getenv("PI_FILE", str(BASE_DIR / ".." / "data" / "pi.txt"))
IMAGE_STORAGE_DIR: Path = Path(os.getenv("IMAGE_STORAGE_DIR", str(BASE_DIR / ".." / "data" / "images"))).resolve()
IMAGE_BASE_URL: str = os.getenv("IMAGE_BASE_URL", "/api/images")
RUNWARE_API_KEY: str = os.getenv("RUNWARE_API_KEY", "")
MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
BFL_API_KEY: str = os.getenv("BFL_API_KEY", "")
BFL_BASE_URL: str = os.getenv("BFL_BASE_URL", "https://api.bfl.ai/v1")

# Use BFL_API_KEY if available, otherwise fall back to RUNWARE_API_KEY for backward compatibility
if not BFL_API_KEY and not RUNWARE_API_KEY:
    raise ValueError("BFL_API_KEY or RUNWARE_API_KEY is not configured in environment variables")
