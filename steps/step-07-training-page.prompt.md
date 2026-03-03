# Step 7 — Training Page

## Goal
Build the Training page: a mobile-friendly digit input that gives live green/red feedback per digit, tracks the current position, and lets the user reset or jump to any position.

## Context to paste at the start of the session
> "I'm building IZY PIZY, a pi memorization web app. Frontend: Svelte + Vite + Tailwind CSS. Backend: FastAPI. Steps 1–6 are done. We are at step 7: the Training page."

---

## Atomic tasks

### 7.1 — Build the main training UI in `Training.svelte`
State to track:
- `currentPosition` (starts at 0, persisted in `localStorage`)
- `lastResult`: `null | "correct" | "wrong"`
- `expectedDigit`: shown only after a wrong answer

Layout:
```
┌──────────────────────────────┐
│   Position: 42               │
│                              │
│   [     big digit input    ] │← large, single-char input
│                              │
│   ✅ Correct!                │← or ❌ Wrong! Expected: 5
│                              │
│          [Reset]  [Jump to…] │
└──────────────────────────────┘
```

### 7.2 — Handle digit input
- The input field accepts a single character
- On each keystroke:
  1. Call `verifyDigit({ position: currentPosition, digit: value })` from `api.js`
  2. If correct: flash green, increment `currentPosition`, clear input
  3. If wrong: flash red, show expected digit, do NOT advance (wait for correct input)
- The input is always focused (re-focus after each keypress)

### 7.3 — Persist position in `localStorage`
- On mount, read `currentPosition` from `localStorage` (default 0)
- On every position change, write to `localStorage`
- So refreshing the page resumes where you left off

### 7.4 — Reset and Jump controls
- **Reset** button: sets position back to 0, clears feedback
- **Jump to…** button: opens a small popover/input asking for a position number (0–999), validates it, and sets `currentPosition`

### 7.5 — Progress display
Above the input, show a small read-only preview of the last 5 digits the user got right (greyed out) + the current position in bold. This helps maintain context while reciting.

---

## Files created / modified in this step
- `frontend/src/pages/Training.svelte` ← replaced stub

## Verification
- Open page → focuses input automatically
- Type `3` (correct for position 0) → green flash, position advances to 1
- Type `9` (wrong for position 1, which should be `1`) → red flash, expected `1` shown, position stays at 1
- Type correct digit → advances
- Refresh page → position is remembered
- Click Reset → position back to 0
- Click "Jump to…" → enter 50 → position jumps to 50
- Works on mobile: large tap target, keyboard pops up naturally
