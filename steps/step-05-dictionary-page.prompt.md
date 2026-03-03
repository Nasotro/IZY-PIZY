# Step 5 — Dictionary Page

## Goal
Build the fully functional Dictionary page: a 10×10 responsive grid of all 100 number pairs, with the ability to view, add, edit, and delete words for each number.

## Context to paste at the start of the session
> "I'm building IZY PIZY, a pi memorization web app. Frontend: Svelte + Vite + Tailwind CSS. Backend: FastAPI. Steps 1–4 are done (scaffold, DB, API, frontend shell). We are at step 5: the Dictionary page."

---

## Atomic tasks

### 5.1 — Build the 10×10 grid in `Dictionary.svelte`
- On mount, call `getDictionary()` from `api.js`
- Render a `10×10` CSS grid (Tailwind `grid grid-cols-10`)
- Each cell shows the 2-digit number and a preview of its first word (or a muted "—" if empty)
- Empty cells have a visually distinct style (e.g. dashed border, muted text)

### 5.2 — Create `WordModal.svelte` component
A reusable modal / bottom-sheet component:
- Props: `number` (e.g. `"07"`), `words` (array), `onClose`
- Shows the number as a large heading
- Lists all existing words as chips with a delete (×) button each
- Has an input + "Add" button at the bottom
- On mobile: slides up from the bottom (`fixed bottom-0`); on desktop: centered modal

### 5.3 — Wire modal open/close into the grid
- Clicking any cell in the grid opens `WordModal.svelte` for that number
- Adding a word calls `addWord(number, word)` then refreshes only that entry
- Deleting a word calls `deleteWord(id)` then refreshes only that entry
- Clicking outside the modal (or pressing Escape) closes it

### 5.4 — (Optional) Inline word editing
Inside the modal, clicking an existing word chip switches it to an `<input>` for editing, with a Save button that calls `updateWord(id, newWord)`.

---

## Files created / modified in this step
- `frontend/src/pages/Dictionary.svelte` ← replaced stub
- `frontend/src/components/WordModal.svelte` ← new

## Verification
- Page loads with 100 cells, all empty initially
- Click cell "07" → modal opens labelled "07"
- Add word "lune" → appears as chip immediately
- Refresh page → "lune" still there (persisted in DB)
- Delete "lune" → chip disappears
- Grid cell for "07" updates to show "lune" preview
- On a narrow screen (≤640px), modal appears at the bottom
