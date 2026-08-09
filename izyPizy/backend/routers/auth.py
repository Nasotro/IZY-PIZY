from fastapi import APIRouter, Header, HTTPException
from firebase_admin import auth
from pydantic import BaseModel

import config

router = APIRouter(prefix="/api", tags=["auth"])


class UserInfo(BaseModel):
    uid: str
    email: str | None = None
    display_name: str | None = None


@router.get("/auth/verify", response_model=UserInfo)
async def verify_token(authorization: str = Header(None)):
    if config.LOCAL_MODE:
        return UserInfo(
            uid=config.LOCAL_MODE_UID,
            email=None,
            display_name=config.LOCAL_MODE_DISPLAY_NAME,
        )

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")

    token = authorization[7:]

    try:
        decoded = auth.verify_id_token(token)
        return UserInfo(
            uid=decoded["uid"],
            email=decoded.get("email"),
            display_name=decoded.get("name"),
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")