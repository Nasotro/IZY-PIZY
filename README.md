# IZY PIZY

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Svelte](https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00)](https://svelte.dev/)
[![Vite](https://img.shields.io/badge/Vite-593D88?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)

A modern web application for memorizing π (Pi) digits. Features spaced repetition, progress tracking, and a clean, responsive interface.

## Features

- **Digit Memorization**: Learn π digits through interactive exercises
- **Progress Tracking**: Monitor your improvement over time
- **Spaced Repetition**: Optimized learning algorithm
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Database | SQLite |
| Frontend | Svelte |
| Build Tool | Vite |
| Styling | Tailwind CSS |

## Project Structure

```
izyPizy/
├── backend/          # FastAPI server
│   ├── main.py       # Entry point
│   └── requirements.txt
├── frontend/         # Svelte app
│   ├── src/
│   └── package.json
└── deploy/           # Production configs
    ├── nginx/
    └── systemd/
```

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

#### Backend

```bash
cd izyPizy/backend
pip install -r requirements.txt
uvicorn main:app --reload
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

#### Frontend

```bash
cd izyPizy/frontend
npm install
npm run dev
```

- App: `http://localhost:5173`
- Hot reload enabled

## Production Deployment

Ready-to-use configuration files are available in the `deploy/` directory:

- **Nginx**: Reverse proxy configuration
- **Systemd**: Service management

## License

MIT
