import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app

from database import init_db
from routers import pi, dictionary, stories, training, auth, images
import config

# Load Firebase credentials from environment variable
cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
FIREBASE_ENABLED = False
if cred_json:
    cred = credentials.Certificate(json.loads(cred_json))
    initialize_app(cred)
    FIREBASE_ENABLED = True
else:
    # Fallback for local development (optional)
    cred_path = os.path.join(os.path.dirname(__file__), "firebase-creds.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        initialize_app(cred)
        FIREBASE_ENABLED = True
    elif config.LOCAL_MODE:
        # Local mode: no Firebase needed; auth is handled locally.
        print("[local-mode] Firebase not configured; using local auth (offline mode).")
    else:
        raise ValueError("Firebase credentials not found in environment variables or local file.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="IZY PIZY API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pi.router, prefix="/api")
app.include_router(dictionary.router, prefix="/api")
app.include_router(stories.router, prefix="/api")
app.include_router(training.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(images.router, prefix="/api")


@app.get("/api/health")
def health_check():
    return {"status": "ok", "local_mode": config.LOCAL_MODE}
