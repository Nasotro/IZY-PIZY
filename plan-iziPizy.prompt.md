# Plan: Pi Memorization Training Website

A single-user web app with a Python backend, SQLite database, and a Svelte + Vite frontend, self-hosted on your Linux server behind Nginx, with your OVH domain pointed at it via DNS. The UI is mobile-first and designed to be usable comfortably on a phone.

**Key decisions:** Python + FastAPI (modern, fast, great auto-generated API docs) · SQLite (zero config, single file, easy to back up) · Svelte + Vite + Tailwind CSS (small bundle, reactive UI, excellent mobile experience) · Nginx + Uvicorn + Systemd for production deployment · Let's Encrypt for free HTTPS.

---

## Steps

1. **Project structure** — Create a clean folder layout: `backend/` for FastAPI, `frontend/` for the Svelte + Vite app (built to `frontend/dist/`), a `data/` folder for the SQLite file, and a `pi.txt` hardcoded with the first 1000 digits.

2. **Database schema (SQLite, 3 tables)**
   - `dictionary_numbers`: columns `number` (TEXT, primary key, e.g. `"07"`) — one row per 2-digit pair
   - `dictionary_words`: columns `id` (INTEGER PK), `number` (TEXT, FK → `dictionary_numbers`), `word` (TEXT) — one row per word, allowing multiple words per number
   - `stories`: columns `id` (INTEGER PK), `position` (INTEGER — which block of 10 digits, 0-indexed), `sentence` (TEXT), `word_0` through `word_4` (TEXT — the 5 words)

3. **Backend API (FastAPI)**
   Build REST endpoints:
   - `GET /api/pi?start=0&length=100` — return a slice of pi digits
   - `GET /api/dictionary` — return all numbers with their list of associated words
   - `POST /api/dictionary/{number}/words` — add a word to a number
   - `PUT /api/dictionary/words/{word_id}` — edit a word
   - `DELETE /api/dictionary/words/{word_id}` — delete a specific word
   - `GET/POST/PUT/DELETE /api/stories` — CRUD for stories (linked to a `position`)
   - `POST /api/train/verify` — receive a digit + position, return correct/wrong + the expected digit

4. **Training page** — A large digit input area. The user types a digit; the app instantly calls the verify endpoint and colors the input green (correct) or red (wrong). A progress counter shows current position. A "reset" button restarts from 0 or a chosen position.

5. **Dictionary page** — A responsive grid showing all 100 pairs (00–99), optimized for both desktop and mobile. Each cell displays the number and all its associated words as chips/tags. Tapping a cell opens a bottom-sheet (mobile) or modal (desktop) to add, edit, or delete words for that number. Empty cells are visually distinct.

6. **Book page** — Lists stories grouped by their position (e.g. position 0 = digits 1–10). Each story card shows the 5 words and the corresponding 10 digits above them. An "Add story" form lets you pick a position and enter the 5 words.

7. **Frontend (Svelte + Vite + Tailwind CSS)** — Three Svelte page components (`Training.svelte`, `Dictionary.svelte`, `Book.svelte`) wired with a lightweight client-side router (e.g. `svelte-routing` or `@sveltejs/kit` file-based routing). Tailwind CSS handles all styling with a mobile-first approach. A persistent bottom navigation bar on mobile and a top nav on desktop. All API calls use `fetch()` to the FastAPI backend. The app is built to static files (`dist/`) served by Nginx.

8. **Local deployment on your Linux server**
   - Run the FastAPI app with **Uvicorn** on `localhost:8000`
   - Create a **Systemd service** file so the app auto-starts on reboot
   - Configure **Nginx** as a reverse proxy on port 80/443
   - Run **Certbot** (Let's Encrypt) to get and auto-renew a free TLS certificate for your domain

9. **DNS configuration** — In the OVH DNS zone for your domain, add an **A record** pointing to your Linux server's public IP. Propagation takes up to 24h but usually under 1h.

---

## Verification

- Navigate to `https://yourdomain.com` — all 3 pages load
- Training: type correct digits → green feedback, wrong digit → red, position advances
- Dictionary: add a word, refresh page → word persists
- Book: add a story at position 2, check that digits 21–30 appear above the words
- Server reboot → app comes back up automatically via Systemd

---

## Key Decisions

- **FastAPI over Flask**: automatic validation, built-in `/docs` page to debug the API, async support if needed later
- **SQLite over PostgreSQL**: no server process, single-file backup (`cp data/pizy.db backup/`), sufficient for one user
- **Svelte over React/Vue**: smaller runtime bundle (better mobile performance), simpler reactive syntax, no virtual DOM overhead — and Vite gives a fast dev experience with hot module reload
- **Tailwind CSS**: utility-first approach makes mobile-first responsive design fast and consistent without writing custom CSS
- **Nginx over serving directly**: handles HTTPS termination, static files, and protects Uvicorn


---

## File Structure

```
izyPizy/
  data/
    pi.txt                        ← first 1000 digits of pi
    izypizy.db                    ← SQLite database (git-ignored)
  backend/
    .env                          ← DATABASE_URL, PI_FILE (git-ignored)
    config.py                     ← reads .env
    main.py                       ← FastAPI app entry point + lifespan
    requirements.txt
    schema.sql                    ← CREATE TABLE statements
    database.py                   ← init_db(), get_db()
    models/
      dictionary.py               ← Pydantic models for dictionary
      stories.py                  ← Pydantic models for stories
      training.py                 ← Pydantic models for training
    routers/
      pi.py                       ← GET /api/pi
      dictionary.py               ← GET/POST/PUT/DELETE /api/dictionary
      stories.py                  ← GET/POST/PUT/DELETE /api/stories
      training.py                 ← POST /api/train/verify
  frontend/
    vite.config.js                ← includes /api proxy to localhost:8000
    tailwind.config.js
    postcss.config.js
    src/
      app.css                     ← Tailwind base imports
      App.svelte                  ← router root
      lib/
        api.js                    ← all fetch() wrappers
      pages/
        Training.svelte
        Dictionary.svelte
        Book.svelte
      components/
        Nav.svelte                ← bottom nav (mobile) / top nav (desktop)
        WordModal.svelte          ← add/edit/delete words for a number
        StoryCard.svelte          ← single story display card
        StoryForm.svelte          ← add/edit story form
    dist/                         ← production build output (git-ignored)
  deploy/
    izypizy.service               ← Systemd unit file
    nginx-izypizy.conf            ← Nginx server block
  steps/
    step-01-project-scaffold.prompt.md
    step-02-database-schema.prompt.md
    step-03a-api-pi-dictionary.prompt.md
    step-03b-api-stories-training.prompt.md
    step-04-frontend-scaffold.prompt.md
    step-05-dictionary-page.prompt.md
    step-06-book-page.prompt.md
    step-07-training-page.prompt.md
    step-08-deployment.prompt.md
    step-09-dns.prompt.md
  README.md
```


