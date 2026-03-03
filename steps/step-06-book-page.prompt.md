# Step 6 — Book Page

## Goal
Build the Book page: a list of story cards grouped by position, each showing the 10 corresponding pi digits above the 5 words, plus a form to add and edit stories.

## Context to paste at the start of the session
> "I'm building IZY PIZY, a pi memorization web app. Frontend: Svelte + Vite + Tailwind CSS. Backend: FastAPI. Steps 1–5 are done. We are at step 6: the Book page."

---

## Atomic tasks

### 6.1 — Build the story list in `Book.svelte`
- On mount, call `getStories()` from `api.js`
- Group stories by `position` and sort ascending
- For each story, render a `StoryCard` component

### 6.2 — Create `StoryCard.svelte` component
Props: `story` (full story object), `piDigits` (pre-fetched slice), `onEdit`, `onDelete`

Card layout:
```
Position 3  (digits 31–40: 5897932384)
┌──────────────────────────────────────┐
│  59   89   79   32   38   4 (extra)  │← digits above each word
│ chat  chien  rose  mine  eau         │← the 5 words
│                                      │
│ Sentence: "Le chat du chien..."      │
│                            [Edit] [Delete]
└──────────────────────────────────────┘
```
- Fetch the 10 digits for this position using `getPi({ start: position*10, length: 10 })`

### 6.3 — Create `StoryForm.svelte` component
A form (used for both adding and editing):
- Fields: `position` (number input), `word_0` through `word_4` (5 text inputs), `sentence` (optional textarea)
- Shows a live preview of the 10 pi digits for the chosen position as the user types the position number
- Submit calls `createStory` or `updateStory` depending on mode
- Cancel button closes the form

### 6.4 — Wire add/edit/delete into `Book.svelte`
- "Add Story" button at the top opens `StoryForm` in create mode
- Clicking "Edit" on a card opens `StoryForm` pre-filled with that story's data
- Clicking "Delete" on a card calls `deleteStory(id)` and removes it from the list
- After save: list re-fetches and form closes

---

## Files created / modified in this step
- `frontend/src/pages/Book.svelte` ← replaced stub
- `frontend/src/components/StoryCard.svelte` ← new
- `frontend/src/components/StoryForm.svelte` ← new

## Verification
- Page loads with empty message when no stories exist
- Click "Add Story", fill form for position 0 → card appears with digits 3141592653 above the 5 words
- Edit the story → changes persist after refresh
- Delete the story → list is empty again
- On mobile: form inputs are comfortably tappable (min height 44px)
