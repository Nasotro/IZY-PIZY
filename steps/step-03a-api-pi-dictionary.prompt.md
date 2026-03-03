# Step 3 — Backend API: Pi & Dictionary Endpoints

## Goal
Implement the `/api/pi` and all `/api/dictionary` endpoints as a FastAPI router.

## Context to paste at the start of the session
> "I'm building IZY PIZY, a pi memorization web app. Stack: FastAPI + aiosqlite, SQLite database. Steps 1–2 are done (scaffold + schema). We are at step 3a: the pi and dictionary API routers."

---

## Atomic tasks

### 3a.1 — Create `routers/pi.py`
A single endpoint:
- `GET /api/pi?start=0&length=10`
  - Reads `pi.txt` from `config.PI_FILE`
  - Returns `{"digits": "3141592653", "start": 0, "length": 10}`
  - Validates: `start >= 0`, `length` between 1 and 1000, `start + length <= len(pi)`

### 3a.2 — Create `routers/dictionary.py`
Five endpoints:
- `GET /api/dictionary` — returns all 100 numbers with their word lists:
  ```json
  [{"number": "07", "words": [{"id": 1, "word": "lune"}]}, …]
  ```
- `POST /api/dictionary/{number}/words` — body: `{"word": "lune"}` → adds word, returns new word object
- `PUT /api/dictionary/words/{word_id}` — body: `{"word": "soleil"}` → updates word
- `DELETE /api/dictionary/words/{word_id}` → deletes word, returns `{"ok": true}`

### 3a.3 — Create Pydantic models
Create `models/dictionary.py` with:
- `WordCreate(BaseModel)`: `word: str`
- `WordOut(BaseModel)`: `id: int`, `word: str`
- `DictionaryEntry(BaseModel)`: `number: str`, `words: list[WordOut]`

### 3a.4 — Register routers in `main.py`
Mount both routers under `/api` prefix.

---

## Files created / modified in this step
- `backend/routers/pi.py` ← new
- `backend/routers/dictionary.py` ← new
- `backend/models/dictionary.py` ← new
- `backend/main.py` ← modified (register routers)

## Verification
- `GET /api/pi?start=0&length=10` → `{"digits":"3141592653",...}`
- `GET /api/dictionary` → array of 100 entries, all with empty `words` initially
- `POST /api/dictionary/07/words` `{"word":"lune"}` → `{"id":1,"word":"lune"}`
- `GET /api/dictionary` → entry `"07"` now has one word
- `PUT /api/dictionary/words/1` `{"word":"soleil"}` → word is updated
- `DELETE /api/dictionary/words/1` → word is gone
- Check `/docs` (FastAPI auto-docs) for all endpoints
