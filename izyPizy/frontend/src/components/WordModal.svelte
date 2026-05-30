<script>
  import { onMount, tick } from 'svelte';
  import { addWord, updateWord, deleteWord } from '../lib/api.js';

  export let number = '';
  export let words = [];
  export let onClose = () => {};
  export let onUpdate = (_number) => {};

  let newWord = '';
  let editingId = null;
  let editingValue = '';
  let error = '';
  let inputEl;
  let adding = false;
  let deleting = new Set();

  onMount(async () => {
    await tick();
    inputEl?.focus();
  });

  async function handleAdd() {
    const trimmed = newWord.trim();
    if (!trimmed || adding) return;
    const cleaned = trimmed.replace(/^[^\w]+/, '').replace(/[^\w]+$/, '');
    adding = true;
    try {
      await addWord(number, cleaned);
      newWord = '';
      error = '';
      await onUpdate(number);
    } catch (e) {
      error = e.message;
    } finally {
      adding = false;
    }
  }

  async function handleDelete(id) {
    if (deleting.has(id)) return;
    deleting = new Set([...deleting, id]);
    try {
      await deleteWord(id);
      error = '';
      await onUpdate(number);
    } catch (e) {
      error = e.message;
    } finally {
      deleting = new Set([...deleting].filter(x => x !== id));
    }
  }

  function startEdit(id, currentWord) {
    editingId = id;
    editingValue = currentWord;
  }

  async function handleSaveEdit(id) {
    const trimmed = editingValue.trim();
    if (!trimmed) return;
    const cleaned = trimmed.replace(/^[^\w]+/, '').replace(/[^\w]+$/, '');
    try {
      await updateWord(id, cleaned);
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
  on:keydown={handleKeydown}
  role="dialog"
  aria-modal="true"
  aria-label="Words for {number}"
  tabindex="-1"
>
  <!-- Panel: bottom-sheet on mobile, centered modal on desktop -->
  <div
    class="fixed bottom-0 left-0 right-0 z-50 rounded-t-2xl p-5 pb-24 md:p-6 md:pb-6 shadow-2xl max-h-[80vh] overflow-y-auto
           sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:w-96 md:w-[480px] lg:w-[560px] sm:-translate-x-1/2 sm:-translate-y-1/2 sm:rounded-2xl"
    style="background-color: var(--color-dominant);"
    role="document"
  >
    <!-- Header -->
    <div class="mb-4 md:mb-5 flex items-center justify-between">
      <span class="text-4xl md:text-5xl lg:text-6xl font-extrabold text-theme-accent">{number}</span>
      <button
        class="rounded-full p-1 md:p-2 hover:bg-theme-muted/5"
        style="color: var(--color-muted);"
        on:click={onClose}
        aria-label="Close"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 md:h-7 md:w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Word chips -->
    <div class="mb-4 md:mb-5 flex flex-wrap gap-2 md:gap-3 min-h-[2rem]">
      {#if words.length === 0}
        <span class="text-sm md:text-base text-theme-muted/40 italic">No words yet.</span>
      {/if}
      {#each words as w (w.id)}
        {#if editingId === w.id}
          <div class="flex items-center gap-1 md:gap-2">
            <input
              class="rounded border px-2 py-1 md:px-3 md:py-2 text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-theme-accent/40 bg-theme-surface"
              style="border-color: var(--color-accent); color: var(--color-secondary);"
              bind:value={editingValue}
              on:keydown={(e) => e.key === 'Enter' && handleSaveEdit(w.id)}
            />
            <button
              class="rounded px-2 py-1 md:px-3 md:py-2 text-xs md:text-sm hover:opacity-90"
              style="background-color: var(--color-accent); color: var(--color-dominant);"
              on:click={() => handleSaveEdit(w.id)}
            >Save</button>
            <button
              class="rounded px-2 py-1 md:px-3 md:py-2 text-xs md:text-sm hover:bg-theme-muted/10"
              style="background-color: var(--color-surface-alt); color: var(--color-secondary);"
              on:click={() => (editingId = null)}
            >Cancel</button>
          </div>
        {:else}
          <span class="flex items-center gap-1 rounded-full px-3 py-1 md:px-4 md:py-2 text-sm md:text-base font-medium" style="background-color: var(--color-accent); color: var(--color-secondary);">
            <button
              class="hover:text-theme-accent"
              style="color: inherit;"
              on:click={() => startEdit(w.id, w.word)}
              title="Edit"
            >{w.word}</button>
<button
        class="ml-1 hover:text-red-500 disabled:opacity-30"
        style="color: var(--color-muted);"
        on:click={() => handleDelete(w.id)}
        disabled={deleting.has(w.id)}
        aria-label="Delete {w.word}"
      >
        {#if deleting.has(w.id)}
          <span class="inline-block animate-spin">⟳</span>
        {:else}
          ×
        {/if}
      </button>
          </span>
        {/if}
      {/each}
    </div>

    {#if error}
      <p class="mb-2 text-xs md:text-sm text-red-500">{error}</p>
    {/if}

    <!-- Add word input -->
    <div class="flex gap-2 md:gap-3 mt-2">
      <input
        bind:this={inputEl}
        type="text"
        inputmode="text"
        class="flex-1 rounded-lg border px-3 py-3 text-base focus:outline-none focus:ring-2 focus:ring-theme-accent/40 bg-theme-surface"
        style="border-color: var(--color-border-muted); color: var(--color-secondary);"
        placeholder="New word…"
        bind:value={newWord}
        on:keydown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <button
        type="button"
        class="rounded-lg px-5 py-3 text-base font-semibold hover:disabled:opacity-40 flex items-center gap-2"
        style="background-color: var(--color-accent); color: var(--color-dominant);"
        on:click={handleAdd}
        disabled={adding}
      >
        {#if adding}
          <span class="inline-block animate-spin">⟳</span>
        {/if}
        Add
      </button>
    </div>
  </div>
</div>
