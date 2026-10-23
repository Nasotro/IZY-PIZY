"""FLUX.3 video client (image-to-video with keyframes).

Only what the app needs: one call, N keyframes, optional draft mode.

Measured on 2026-10-22 (5s, HD, 960x960, 24fps, 121 frames):
- draft=True  : ~55s, 0 credit billed (preview)
- draft=False : ~76s, 105 credits (~$1.05) — the "reasoning" pass is billed
- draft_enhance on a draft's cache: ~46s, 75 credits (~$0.75)

Draft renders are genuinely softer (2.5 Mbit/s vs 7.9) but more than good
enough to validate a flashcard animation, hence the default.
"""

from __future__ import annotations

import asyncio
import base64
import json
import mimetypes
import time
from pathlib import Path

import httpx

import config

TERMINAL_STATES = {"Ready", "Request Moderated", "Content Moderated", "Error", "Task not found"}


def file_to_data_url(path: str | Path) -> str:
    """Encode a local image as a data: URL (FLUX accepts URLs or base64)."""
    path = Path(path)
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


async def generate_video_from_keyframes(
    prompt: str,
    keyframes: list[tuple[float, str]],
    output_path: str,
    *,
    duration: int = 5,
    resolution: str = "hd",
    aspect_ratio: str = "1:1",
    draft: bool = True,
    generate_audio: bool = False,
    timeout: float = 900.0,
) -> dict:
    """Submit an i2v job, wait for it and save the mp4.

    ``keyframes`` is a list of ``(seconds, image)`` pairs where image is an
    http(s) URL or a data: URL, in time order. Two keyframes = start + end.
    """
    if config.LOCAL_MODE or not config.BFL_API_KEY:
        raise RuntimeError(
            "Video generation needs a Blackforest API key; it is not available in local mode."
        )
    if not 5 <= duration <= 20:
        raise RuntimeError(f"duration must be between 5 and 20 seconds, got {duration}")

    base_url = config.BFL_BASE_URL.rstrip("/")
    headers = {
        "accept": "application/json",
        "x-key": config.BFL_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "mode": "i2v",
        "prompt": prompt,
        "keyframes": [[float(sec), img] for sec, img in keyframes],
        "duration": int(duration),
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "generate_audio": generate_audio,
        "draft": bool(draft),
    }

    started = time.time()
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(f"{base_url}/flux-3-video", headers=headers, json=payload)
        if r.status_code != 200:
            raise RuntimeError(f"Video submit failed: HTTP {r.status_code} - {r.text[:400]}")
        submitted = r.json()

    polling_url = submitted.get("polling_url")
    if not polling_url:
        raise RuntimeError(f"Unexpected video response: {json.dumps(submitted)[:400]}")

    job_id = submitted.get("id", "unknown")
    print(f"[video] submitted {job_id} draft={draft} duration={duration}s", flush=True)

    last_status = None
    data: dict = {}
    async with httpx.AsyncClient(timeout=60.0) as client:
        while time.time() - started < timeout:
            await asyncio.sleep(3.0)
            poll = await client.get(polling_url, headers={"accept": "application/json", "x-key": config.BFL_API_KEY})
            if poll.status_code != 200:
                raise RuntimeError(f"Video poll failed: HTTP {poll.status_code} - {poll.text[:300]}")
            data = poll.json()
            status = data.get("status")
            if status != last_status:
                print(f"[video] {status} ({time.time() - started:.0f}s)", flush=True)
                last_status = status
            if status in TERMINAL_STATES:
                break

    if last_status != "Ready":
        raise RuntimeError(f"Video generation failed ({last_status}): {json.dumps(data)[:400]}")

    result = data.get("result") or {}
    url = result.get("sample") or result.get("video")
    if not url:
        raise RuntimeError(f"Video result has no sample URL: {json.dumps(result)[:300]}")

    async with httpx.AsyncClient(timeout=300.0) as client:
        dl = await client.get(url)
        if dl.status_code != 200:
            raise RuntimeError(f"Video download failed: HTTP {dl.status_code}")
        Path(output_path).write_bytes(dl.content)

    return {
        "path": output_path,
        "job_id": job_id,
        "elapsed": round(time.time() - started, 1),
        "draft": bool(draft),
        "duration": duration,
        "seed": result.get("seed"),
        "draft_cache": result.get("draft_cache"),
    }
