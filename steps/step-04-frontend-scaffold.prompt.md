# Step 4 — Frontend Scaffold (Svelte + Vite + Tailwind + Router)

## Goal
Set up the Svelte app shell: router, shared layout, navigation bar, and API client utility. No page content yet — just the skeleton every page will plug into.

## Context to paste at the start of the session
> "I'm building IZY PIZY, a pi memorization web app. Frontend stack: Svelte + Vite + Tailwind CSS. The Vite scaffold already exists from step 1. Steps 1–3b are done. We are at step 4: wire up the router, layout, and nav."

---

## Atomic tasks

### 4.1 — Install dependencies
```
npm install svelte-routing
```
Tailwind is already set up from step 1.

### 4.2 — Create the API client utility
Create `src/lib/api.js`:
- A base `apiFetch(path, options)` function that prepends `/api` and handles JSON parsing + error throwing
- Named exports for every endpoint: `getPi`, `getDictionary`, `addWord`, `updateWord`, `deleteWord`, `getStories`, `createStory`, `updateStory`, `deleteStory`, `verifyDigit`

### 4.3 — Create page stub components
Create three minimal stub files (just an `<h1>` for now):
- `src/pages/Training.svelte`
- `src/pages/Dictionary.svelte`
- `src/pages/Book.svelte`

### 4.4 — Update `App.svelte` with routing
Replace `App.svelte` to use `svelte-routing`'s `<Router>`, `<Route>`, and `<Link>` to wire the three pages to `/`, `/dictionary`, and `/book`.

### 4.5 — Create `Nav.svelte` component
Create `src/components/Nav.svelte`:
- **Mobile** (default): fixed bottom bar with 3 icon+label buttons (Training, Dictionary, Book) using Tailwind
- **Desktop** (`md:` breakpoint): horizontal top bar
- Active route is visually highlighted

### 4.6 — Configure Vite dev proxy
Update `vite.config.js` to proxy `/api` requests to `http://localhost:8000` during development so the frontend and backend can run separately without CORS issues.

---

## Files created / modified in this step
- `frontend/src/lib/api.js` ← new
- `frontend/src/pages/Training.svelte` ← new (stub)
- `frontend/src/pages/Dictionary.svelte` ← new (stub)
- `frontend/src/pages/Book.svelte` ← new (stub)
- `frontend/src/components/Nav.svelte` ← new
- `frontend/src/App.svelte` ← modified
- `frontend/vite.config.js` ← modified (proxy)

## Verification
- `npm run dev` → no errors
- Navigate to `http://localhost:5173/` → Training stub renders, Nav visible
- Navigate to `/dictionary` and `/book` → correct stubs render
- Bottom nav visible on narrow screen, top nav on wide screen
- `fetch('/api/health')` from browser console → `{"status":"ok"}` (via proxy)
