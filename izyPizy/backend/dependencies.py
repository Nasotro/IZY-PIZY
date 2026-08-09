from fastapi import Depends, Header, HTTPException
from firebase_admin import auth
from pydantic import BaseModel

import config


class CurrentUser(BaseModel):
    uid: str
    email: str | None = None
    display_name: str | None = None


async def get_current_user(authorization: str = Header(None)) -> CurrentUser:
    if config.LOCAL_MODE:
        # Local mode: no Firebase. Accept any Bearer token (or none) and fall
        # back to the fixed local user so every endpoint works offline.
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:]
            try:
                decoded = auth.verify_id_token(token)
                return CurrentUser(
                    uid=decoded["uid"],
                    email=decoded.get("email"),
                    display_name=decoded.get("name"),
                )
            except Exception:
                pass  # Not a valid Firebase token -> local user below
        return CurrentUser(
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
        return CurrentUser(
            uid=decoded["uid"],
            email=decoded.get("email"),
            display_name=decoded.get("name"),
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
