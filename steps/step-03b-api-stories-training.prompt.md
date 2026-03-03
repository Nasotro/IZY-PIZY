# Step 3b — Backend API: Stories & Training Endpoints

## Goal
Implement the `/api/stories` CRUD router and the `/api/train/verify` endpoint.

## Context to paste at the start of the session
> "I'm building IZY PIZY, a pi memorization web app. Stack: FastAPI + aiosqlite, SQLite database. Steps 1–3a are done (scaffold, schema, pi & dictionary API). We are at step 3b: stories and training API routers."

---

## Atomic tasks

### 3b.1 — Create Pydantic models in `models/stories.py`
- `StoryCreate(BaseModel)`: `position: int`, `sentence: str | None`, `word_0..4: str`
- `StoryOut(BaseModel)`: same fields + `id: int`

### 3b.2 — Create `routers/stories.py`
Four endpoints:
- `GET /api/stories` — returns all stories ordered by `position`; optionally filter by `?position=2`
- `POST /api/stories` — body: `StoryCreate` → inserts, returns `StoryOut`
- `PUT /api/stories/{story_id}` — body: `StoryCreate` → updates, returns `StoryOut`
- `DELETE /api/stories/{story_id}` → deletes, returns `{"ok": true}`

### 3b.3 — Create Pydantic models in `models/training.py`
- `VerifyRequest(BaseModel)`: `position: int` (0-indexed digit position in pi, e.g. 0 = first digit after decimal)
- `VerifyResponse(BaseModel)`: `correct: bool`, `expected: str` (the digit), `position: int`

### 3b.4 — Create `routers/training.py`
One endpoint:
- `POST /api/train/verify` — body: `{"position": 5, "digit": "9"}`:
  1. Reads `pi.txt`
  2. Compares submitted digit against `pi[position]`
  3. Returns `{"correct": true/false, "expected": "9", "position": 5}`

### 3b.5 — Register new routers in `main.py`

---

## Files created / modified in this step
- `backend/models/stories.py` ← new
- `backend/models/training.py` ← new
- `backend/routers/stories.py` ← new
- `backend/routers/training.py` ← new
- `backend/main.py` ← modified (register routers)

## Verification
- `POST /api/stories` with valid body → story saved and returned with `id`
- `GET /api/stories` → list with the new story
- `GET /api/stories?position=0` → only stories at position 0
- `PUT /api/stories/1` → story updated
- `DELETE /api/stories/1` → story gone
- `POST /api/train/verify` `{"position":0,"digit":"3"}` → `{"correct":true,"expected":"3",...}`
- `POST /api/train/verify` `{"position":0,"digit":"5"}` → `{"correct":false,"expected":"3",...}`
