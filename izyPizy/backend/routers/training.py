from fastapi import APIRouter, HTTPException

import config
from models.training import VerifyRequest, VerifyResponse

router = APIRouter()

_pi_digits: str | None = None


def _load_pi() -> str:
    global _pi_digits
    if _pi_digits is None:
        with open(config.PI_FILE, encoding="utf-8") as f:
            _pi_digits = "".join(ch for ch in f.read() if ch.isdigit())
    return _pi_digits


@router.post("/train/verify", response_model=VerifyResponse)
def verify_digit(body: VerifyRequest):
    digits = _load_pi()
    if body.position < 0 or body.position >= len(digits):
        raise HTTPException(
            status_code=400,
            detail=f"position {body.position} out of range (0–{len(digits) - 1})",
        )
    expected = digits[body.position]
    return VerifyResponse(
        correct=body.digit == expected,
        expected=expected,
        position=body.position,
    )
