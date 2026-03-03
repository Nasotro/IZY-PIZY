# Step 2 — Database Schema

## Goal
Define and initialize the SQLite database with all 3 tables and seed the `dictionary_numbers` table with all 100 pairs (00–99).

## Context to paste at the start of the session
> "I'm building IZY PIZY, a pi memorization web app. Stack: FastAPI + aiosqlite backend, SQLite database. Step 1 (scaffold) is done. We are at step 2: define the database schema."

---

## Atomic tasks

### 2.1 — Write `schema.sql`
Create `izyPizy/backend/schema.sql` with the 3 `CREATE TABLE IF NOT EXISTS` statements:

**`dictionary_numbers`**
- `number` TEXT PRIMARY KEY — the 2-digit string, e.g. `"07"`

**`dictionary_words`**
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `number` TEXT NOT NULL REFERENCES `dictionary_numbers(number)` ON DELETE CASCADE
- `word` TEXT NOT NULL

**`stories`**
- `id` INTEGER PRIMARY KEY AUTOINCREMENT
- `position` INTEGER NOT NULL — 0-indexed block of 10 digits (position 0 = digits 1–10)
- `sentence` TEXT — optional free-text summary
- `word_0` TEXT NOT NULL
- `word_1` TEXT NOT NULL
- `word_2` TEXT NOT NULL
- `word_3` TEXT NOT NULL
- `word_4` TEXT NOT NULL

### 2.2 — Write `database.py`
Create `izyPizy/backend/database.py` with:
- An async function `init_db()` that:
  1. Opens/creates the SQLite file at the path from `config.py`
  2. Executes `schema.sql`
  3. Seeds `dictionary_numbers` with all values `"00"` through `"99"` using `INSERT OR IGNORE`
- A dependency function `get_db()` that yields an `aiosqlite` connection (for use with FastAPI `Depends`)

### 2.3 — Wire `init_db()` into `main.py`
Update `backend/main.py` to call `init_db()` on app startup using a FastAPI `lifespan` context.

---

## Files created / modified in this step
- `backend/schema.sql` ← new
- `backend/database.py` ← new
- `backend/main.py` ← modified (add lifespan)

## Verification
- Start the backend: `uvicorn main:app --reload`
- Inspect the DB: `sqlite3 data/izypizy.db ".tables"` → should show all 3 tables
- `sqlite3 data/izypizy.db "SELECT count(*) FROM dictionary_numbers"` → `100`
- Restart the server a second time → no duplicate seed errors (INSERT OR IGNORE)
