<script>
  import { addWord, updateWord, deleteWord } from '../lib/api.js';

  export let number = '';
  export let words = [];
  export let onClose = () => {};
  export let onUpdate = () => {};

  let newWord = '';
  let editingId = null;
  let editingValue = '';
  let error = '';

  async function handleAdd() {
    const trimmed = newWord.trim();
    if (!trimmed) return;
    try {
      await addWord(number, trimmed);
      newWord = '';
      error = '';
      await onUpdate(number);
    } catch (e) {
      error = e.message;
    }
  }

  async function handleDelete(id) {
    try {
      await deleteWord(id);
      error = '';
      await onUpdate(number);
    } catch (e) {
      error = e.message;
    }
  }

  function startEdit(id, currentWord) {
    editingId = id;
    editingValue = currentWord;
  }

  async function handleSaveEdit(id) {
    const trimmed = editingValue.trim();
    if (!trimmed) return;
    try {
      await updateWord(id, trimmed);
      editingId = null;
      editingValue = '';
      error = '';
      await onUpdate(number);
    } catch (e) {
      error = e.message;
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') onClose();
  }

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) onClose();
  }
</script>

<svelte:window on:keydown={handleKeydown} />

<!-- Backdrop -->
<div
  class="fixed inset-0 z-40 bg-black/40"
  on:click={handleBackdropClick}
  role="dialog"
  aria-modal="true"
  aria-label="Words for {number}"
>
  <!-- Panel: bottom-sheet on mobile, centered modal on desktop -->
  <div
    class="fixed bottom-0 left-0 right-0 z-50 rounded-t-2xl bg-white p-6 shadow-2xl
           sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:w-96 sm:-translate-x-1/2 sm:-translate-y-1/2 sm:rounded-2xl"
    role="document"
  >
    <!-- Header -->
    <div class="mb-4 flex items-center justify-between">
      <span class="text-4xl font-extrabold text-indigo-600">{number}</span>
      <button
        class="rounded-full p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
        on:click={onClose}
        aria-label="Close"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Word chips -->
    <div class="mb-4 flex flex-wrap gap-2 min-h-[2rem]">
      {#if words.length === 0}
        <span class="text-sm text-gray-400 italic">No words yet.</span>
      {/if}
      {#each words as w (w.id)}
        {#if editingId === w.id}
          <div class="flex items-center gap-1">
            <input
              class="rounded border border-indigo-300 px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              bind:value={editingValue}
              on:keydown={(e) => e.key === 'Enter' && handleSaveEdit(w.id)}
              autofocus
            />
            <button
              class="rounded bg-indigo-600 px-2 py-1 text-xs text-white hover:bg-indigo-700"
              on:click={() => handleSaveEdit(w.id)}
            >Save</button>
            <button
              class="rounded bg-gray-200 px-2 py-1 text-xs text-gray-600 hover:bg-gray-300"
              on:click={() => (editingId = null)}
            >Cancel</button>
          </div>
        {:else}
          <span class="flex items-center gap-1 rounded-full bg-indigo-100 px-3 py-1 text-sm font-medium text-indigo-800">
            <button
              class="hover:text-indigo-600"
              on:click={() => startEdit(w.id, w.word)}
              title="Edit"
            >{w.word}</button>
            <button
              class="ml-1 text-indigo-400 hover:text-red-500"
              on:click={() => handleDelete(w.id)}
              aria-label="Delete {w.word}"
            >×</button>
          </span>
        {/if}
      {/each}
    </div>

    {#if error}
      <p class="mb-2 text-xs text-red-500">{error}</p>
    {/if}

    <!-- Add word input -->
    <div class="flex gap-2">
      <input
        class="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
        placeholder="New word…"
        bind:value={newWord}
        on:keydown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <button
        class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
        on:click={handleAdd}
        disabled={!newWord.trim()}
      >Add</button>
    </div>
  </div>
</div>
