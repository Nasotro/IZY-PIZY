from fastapi import APIRouter, HTTPException, Query

import config

router = APIRouter()

_pi_digits: str | None = None


def _load_pi() -> str:
    global _pi_digits
    if _pi_digits is None:
        with open(config.PI_FILE, encoding="utf-8") as f:
            # Strip whitespace / newlines, keep only digit characters
            _pi_digits = "".join(ch for ch in f.read() if ch.isdigit())
    return _pi_digits


@router.get("/pi")
def get_pi(
    start: int = Query(default=0, ge=0),
    length: int = Query(default=10, ge=1, le=1000),
):
    digits = _load_pi()
    if start + length > len(digits):
        raise HTTPException(
            status_code=400,
            detail=f"start + length ({start + length}) exceeds available digits ({len(digits)})",
        )
    return {"digits": digits[start : start + length], "start": start, "length": length}
