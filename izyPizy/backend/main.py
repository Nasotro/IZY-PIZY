import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, initialize_app

from database import init_db
from routers import pi, dictionary, stories, training, auth, images

# Load Firebase credentials from environment variable
cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
if cred_json:
    cred = credentials.Certificate(json.loads(cred_json))
else:
    # Fallback for local development (optional)
    cred_path = os.path.join(os.path.dirname(__file__), "firebase-creds.json")
    if os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
    else:
        raise ValueError("Firebase credentials not found in environment variables or local file.")

initialize_app(cred)


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
    return {"status": "ok"}
