# IZY PIZY

A pi memorization web app. Stack: FastAPI · SQLite · Svelte + Vite + Tailwind CSS.

## Run locally

### Backend

```bash
cd izyPizy/backend
pip install -r requirements.txt
uvicorn main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Frontend

```bash
cd izyPizy/frontend
npm install
npm run dev
# App available at http://localhost:5173
```

## Production

See `deploy/` for Systemd and Nginx configuration files.
