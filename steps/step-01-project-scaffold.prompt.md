# Step 1 — Project Scaffold

## Goal
Create the full folder skeleton and initialize both the backend and frontend toolchains so every subsequent step has a place to land.

## Context to paste at the start of the session
> "I'm building IZY PIZY, a pi memorization web app. Stack: FastAPI backend, Svelte + Vite + Tailwind CSS frontend, SQLite database. I'm on a Linux server. We are at step 1: scaffold the project."

---

## Atomic tasks

### 1.0 — Initialize the git repository
In the project root:
```bash
git init
```
Create a `.gitignore` with at minimum:
```
data/izypizy.db
backend/.env
backend/.venv/
frontend/node_modules/
frontend/dist/
```
Then make the first commit: `git add -A && git commit -m "chore: init repository"`

### 1.1 — Create the folder structure
Create the following empty directories (with `.gitkeep` where needed):
```
izyPizy/
  backend/
    routers/
    models/
  frontend/         ← Svelte + Vite project will live here
  data/             ← SQLite file will live here
  deploy/           ← Nginx + Systemd config files
```

### 1.2 — Create `pi.txt`
Create `izyPizy/data/pi.txt` containing the first 1000 digits of pi (no spaces, no newlines, starting with `3141592653…`).

### 1.3 — Initialize the Python backend
Inside `izyPizy/backend/`:
- Create `requirements.txt` with: `fastapi`, `uvicorn[standard]`, `aiosqlite`, `python-dotenv`
- Create a minimal `main.py` (FastAPI app entry point, no routes yet, just a health-check `GET /api/health` returning `{"status": "ok"}`)
- Create `.env` with `DATABASE_URL=../data/izypizy.db` and `PI_FILE=../data/pi.txt`
- Create `config.py` that reads `.env`

### 1.4 — Initialize the Svelte + Vite frontend
Inside `izyPizy/frontend/`:
- Run `npm create vite@latest . -- --template svelte` to scaffold the Svelte project
- Install Tailwind CSS and configure it (`tailwind.config.js`, `postcss.config.js`, import in `src/app.css`)
- Install `svelte-routing` for client-side routing
- Strip the default Vite boilerplate (`App.svelte` → just a `<p>Hello IZY PIZY</p>`)

### 1.5 — Create root `README.md`
A short file documenting how to run the project locally:
- `cd backend && pip install -r requirements.txt && uvicorn main:app --reload`
- `cd frontend && npm install && npm run dev`

---

## Files created in this step
- `data/pi.txt`
- `backend/requirements.txt`
- `backend/main.py`
- `backend/.env`
- `backend/config.py`
- `frontend/` (full Vite scaffold)
- `frontend/tailwind.config.js`
- `frontend/postcss.config.js`
- `README.md`

## Verification
- `GET http://localhost:8000/api/health` → `{"status": "ok"}`
- `http://localhost:5173` → blank Svelte page with "Hello IZY PIZY"
- No TypeScript errors, Tailwind classes apply correctly
