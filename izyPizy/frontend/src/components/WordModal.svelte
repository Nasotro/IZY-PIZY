<script>
  import { onMount, tick } from 'svelte';
  import { addWord, updateWord, deleteWord, getWordIcon, generateWordIcon, deleteWordIcon } from '../lib/api.js';

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

  // ---- word icon editor -------------------------------------------------
  let selectedWord = null;     // { id, word }
  let iconState = null;        // GET /icon payload
  let iconDescription = '';
  let iconModel = 'small';
  let iconLoading = false;
  let iconGenerating = false;
  let iconError = '';

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
      if (selectedWord?.id === id) closeIconEditor();
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
    if (e.key === 'Escape') {
      if (selectedWord) closeIconEditor();
      else onClose();
    }
  }

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) onClose();
  }

  async function openIconEditor(w) {
    selectedWord = w;
    iconState = null;
    iconError = '';
    iconDescription = '';
    iconLoading = true;
    try {
      const state = await getWordIcon(w.id);
      iconState = state;
      iconDescription = state.user_description || '';
      iconModel = state.model || 'small';
    } catch (e) {
      iconError = e.message;
    } finally {
      iconLoading = false;
    }
  }

  function closeIconEditor() {
    selectedWord = null;
    iconState = null;
    iconError = '';
  }

  async function handleGenerateIcon() {
    if (!selectedWord || iconGenerating) return;
    iconGenerating = true;
    iconError = '';
    try {
      const result = await generateWordIcon(selectedWord.id, {
        description: iconDescription.trim(),
        model: iconModel,
      });
      iconState = result;
      // every entry spelling the same word now has this icon
      await onUpdate(number);
    } catch (e) {
      iconError = e.message || 'Icon generation failed';
    } finally {
      iconGenerating = false;
    }
  }

  async function handleDeleteIcon() {
    if (!selectedWord || iconGenerating) return;
    iconGenerating = true;
    iconError = '';
    try {
      await deleteWordIcon(selectedWord.id);
      iconState = null;
      await onUpdate(number);
    } catch (e) {
      iconError = e.message;
    } finally {
      iconGenerating = false;
    }
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
    class="fixed bottom-0 left-0 right-0 z-50 rounded-t-2xl p-5 pb-24 md:p-6 md:pb-6 border-retro-thick shadow-retro-xl max-h-[85vh] overflow-y-auto
           sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:w-96 md:w-[480px] lg:w-[560px] sm:-translate-x-1/2 sm:-translate-y-1/2 sm:rounded-2xl"
    style="background-color: var(--color-dominant);"
    role="document"
  >
    <!-- Header -->
    <div class="mb-4 md:mb-5 flex items-center justify-between">
      <span class="text-4xl md:text-5xl lg:text-6xl font-mono font-bold text-theme-accent">{number}</span>
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
              class="input-retro px-2 py-1 md:px-3 md:py-2 text-sm md:text-base"
              bind:value={editingValue}
              on:keydown={(e) => e.key === 'Enter' && handleSaveEdit(w.id)}
            />
            <button
              class="btn-retro btn-retro-primary px-2 py-1 md:px-3 md:py-2 text-xs md:text-sm"
              on:click={() => handleSaveEdit(w.id)}
            >Save</button>
            <button
              class="btn-retro btn-retro-secondary px-2 py-1 md:px-3 md:py-2 text-xs md:text-sm"
              on:click={() => (editingId = null)}
            >Cancel</button>
          </div>
        {:else}
          <span
            class="flex items-center gap-1 rounded-lg border-2 px-2 py-1 md:px-3 md:py-2 text-sm md:text-base font-medium shadow-retro-sm"
            style="background-color: var(--color-surface); border-color: {selectedWord?.id === w.id ? 'var(--color-accent)' : 'var(--color-border)'}; color: var(--color-secondary);"
          >
            <button
              class="hover:text-theme-accent flex items-center gap-1.5"
              style="color: inherit;"
              on:click={() => openIconEditor(w)}
              title={w.has_icon ? 'Edit icon' : 'Create an icon for this word'}
            >
              {#if w.has_icon && w.icon_url}
                <img src={w.icon_url} alt="" class="h-6 w-6 md:h-7 md:w-7 rounded border" style="border-color: var(--color-border-muted); background: white;" />
              {:else}
                <span class="inline-flex h-6 w-6 md:h-7 md:w-7 items-center justify-center rounded border border-dashed text-[10px]" style="border-color: var(--color-border-muted); color: var(--color-muted);">+</span>
              {/if}
              {w.word}
            </button>
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

    <!-- Icon editor -->
    {#if selectedWord}
      <div class="mb-4 rounded-lg border-2 p-3 md:p-4" style="border-color: var(--color-border); background-color: var(--color-surface);">
        <div class="flex items-start gap-3 md:gap-4">
          <div class="h-20 w-20 md:h-24 md:w-24 shrink-0 rounded border-2 flex items-center justify-center overflow-hidden" style="border-color: var(--color-border-muted); background: white;">
            {#if iconGenerating}
              <span class="animate-spin text-2xl">⟳</span>
            {:else if iconState?.icon_url}
              <img src={iconState.icon_url} alt="Icon for {selectedWord.word}" class="h-full w-full object-contain" />
            {:else if iconLoading}
              <span class="animate-spin text-xl">⟳</span>
            {:else}
              <span class="text-xs text-center px-1" style="color: var(--color-muted);">no icon yet</span>
            {/if}
          </div>

          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between gap-2">
              <p class="font-display text-base md:text-lg" style="color: var(--color-secondary);">Icon: {selectedWord.word}</p>
              <button class="text-xs underline" style="color: var(--color-muted);" on:click={closeIconEditor}>close</button>
            </div>

            <label class="block text-xs mt-1 mb-1" style="color: var(--color-muted);">
              Description (optional) — disambiguate the word, e.g. “tuiles de toit en terre cuite”
            </label>
            <textarea
              bind:value={iconDescription}
              rows="2"
              class="w-full input-retro px-2 py-1 text-sm resize-none"
              placeholder="How should this word be drawn?"
              disabled={iconGenerating}
            ></textarea>

            <div class="mt-2 flex flex-wrap items-center gap-2">
              <div class="flex gap-1">
                {#each ['small', 'big'] as tier}
                  <button
                    class="px-2 py-1 rounded border-2 text-xs font-medium"
                    style="border-color: {iconModel === tier ? 'var(--color-accent)' : 'var(--color-border-muted)'}; color: {iconModel === tier ? 'var(--color-accent)' : 'var(--color-secondary)'};"
                    on:click={() => iconModel = tier}
                    disabled={iconGenerating}
                  >{tier === 'small' ? 'Small (~1,4 cr)' : 'Big (~3 cr)'}</button>
                {/each}
              </div>
              <button
                class="btn-retro btn-retro-primary px-3 py-1 text-xs md:text-sm disabled:opacity-50"
                on:click={handleGenerateIcon}
                disabled={iconGenerating || iconLoading}
              >
                {iconGenerating ? 'Drawing…' : (iconState?.has_icon ? 'Regenerate' : 'Create icon')}
              </button>
              {#if iconState?.has_icon}
                <button
                  class="btn-retro btn-retro-secondary px-3 py-1 text-xs md:text-sm disabled:opacity-50"
                  on:click={handleDeleteIcon}
                  disabled={iconGenerating}
                >Delete</button>
              {/if}
            </div>

            {#if iconError}
              <p class="mt-2 text-xs text-red-500">{iconError}</p>
            {/if}
            {#if iconState?.has_icon}
              <p class="mt-2 text-[11px] leading-snug" style="color: var(--color-muted);">
                This icon is shared by every dictionary entry spelling “{iconState.word_key}”.
              </p>
            {/if}
          </div>
        </div>
      </div>
    {/if}

    <!-- Add word input -->
    <div class="flex gap-2 md:gap-3 mt-2">
      <input
        bind:this={inputEl}
        type="text"
        inputmode="text"
        class="flex-1 input-retro px-3 py-3 text-base"
        placeholder="New word…"
        bind:value={newWord}
        on:keydown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <button
        type="button"
        class="btn-retro btn-retro-primary px-5 py-3 text-base flex items-center gap-2"
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
