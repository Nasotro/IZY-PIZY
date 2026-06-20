<script>
  import { getPi, createStory, updateStory } from '../lib/api.js';
  import Loader from './Loader.svelte';

  /** @type {{ id: number, position: number, sentence?: string, word_0: string, word_1: string, word_2: string, word_3: string, word_4: string } | null} */
  export let story = null;

  /** @type {number | undefined} */
  export let nextPosition = undefined;

  /** @type {(saved: object) => void} */
  export let onSave = () => {};

  /** @type {() => void} */
  export let onCancel = () => {};

  const isEdit = story !== null;

  let position = story
    ? story.position
    : typeof nextPosition === 'number'
      ? nextPosition
      : 0;
  
  let sentence = story?.sentence ?? '';
  
  // Track which word indices in the sentence are selected
  let selectedIndices = [];

  let previewDigits = '';
  let previewLoading = false;
  let saving = false;
  let error = '';
  
  // Step 1: write sentence, Step 2: select words
  let step = isEdit ? 2 : 1;

  // Extract words from sentence for selection
  $: words = sentence.trim() === '' ? [] : sentence.split(/\s+/).map(w => w.replace(/^[^\w]+/, '').replace(/[^\w]+$/, ''));
  
  // If editing and we have words, pre-select the 5 words from the story
  $: if (isEdit && step === 2 && words.length > 0 && selectedIndices.length === 0) {
    const storyWords = [story.word_0, story.word_1, story.word_2, story.word_3, story.word_4];
    const newSelectedIndices = [];
    
    for (const sw of storyWords) {
      const lowerSw = sw.toLowerCase();
      // Find the first unselected word that matches
      for (let i = 0; i < words.length; i++) {
        if (!newSelectedIndices.includes(i) && words[i].toLowerCase() === lowerSw) {
          newSelectedIndices.push(i);
          break;
        }
      }
    }
    
    if (newSelectedIndices.length > 0) {
      selectedIndices = newSelectedIndices;
    }
  }

  function goToStep2() {
    if (sentence.trim() === '') {
      error = 'Please write a story first.';
      return;
    }
    if (words.length < 5) {
      error = 'Your story needs at least 5 words to select from.';
      return;
    }
    error = '';
    step = 2;
  }

  function goBackToStep1() {
    step = 1;
    selectedIndices = [];
    error = '';
  }

  function toggleWord(index) {
    const isSelected = selectedIndices.includes(index);
    
    if (isSelected) {
      // Deselect
      selectedIndices = selectedIndices.filter(i => i !== index);
    } else {
      // Select (only if we have less than 5)
      if (selectedIndices.length < 5) {
        selectedIndices = [...selectedIndices, index];
      }
    }
  }

  async function fetchPreview(pos) {
    if (pos < 0 || pos > 99) { previewDigits = ''; return; }
    previewLoading = true;
    try {
      const data = await getPi(pos * 10, 10);
      previewDigits = data.digits;
    } catch {
      previewDigits = '';
    } finally {
      previewLoading = false;
    }
  }

  // Reactive: fetch preview whenever position changes
  $: fetchPreview(position);

  $: pairs = previewDigits
    ? [0, 1, 2, 3, 4].map((i) => previewDigits.slice(i * 2, i * 2 + 2))
    : ['??', '??', '??', '??', '??'];

  async function handleSubmit() {
    error = '';
    if (selectedIndices.length !== 5) {
      error = 'Please select exactly 5 words from your story.';
      return;
    }
    
    saving = true;
    try {
      // Sort selected indices to maintain sentence order, then map to word_0-word_4
      const sortedIndices = [...selectedIndices].sort((a, b) => a - b);
      const wordObj = {};
      sortedIndices.forEach((idx, order) => {
        wordObj[`word_${order}`] = words[idx];
      });
      
      const payload = {
        position,
        sentence: sentence || null,
        ...wordObj
      };
      const saved = isEdit
        ? await updateStory(story.id, payload)
        : await createStory(payload);
      onSave(saved);
    } catch (e) {
      error = e.message;
    } finally {
      saving = false;
    }
  }

  // Helper: get class for word button based on selection state
  $: wordClasses = words.map((_, i) => {
    const isSel = selectedIndices.includes(i);
    const base = 'inline-block mx-0.5 px-2 py-1 rounded text-sm md:text-base transition-all border';
    if (isSel) {
      return `${base} bg-theme-accent/15 border-2 border-theme-accent text-theme-accent font-bold`;
    }
    return `${base} hover:bg-theme-muted/10 border-transparent`;
  });
</script>

<div class="rounded-2xl border border-[#C75B39]/20 bg-theme-surface p-5 shadow-sm">
  <form on:submit|preventDefault={handleSubmit} class="space-y-4">
    <!-- Pi digit preview -->
    <div class="rounded-lg bg-theme-surface-alt border border-theme-muted/10 px-4 py-3 md:px-5 md:py-4">
      <p class="text-xs md:text-sm text-theme-muted mb-2">
        Pi digits for position {position}&nbsp;
        (digits {position * 10 + 1}–{position * 10 + 10}):
      </p>
      {#if previewLoading}
        <div class="flex justify-center">
          <Loader size="sm" />
        </div>
      {:else}
        <div class="grid grid-cols-5 gap-1 md:gap-2 text-center">
          {#each pairs as pair, i}
            <span class="font-mono text-sm md:text-base font-bold text-theme-accent bg-theme-accent/5 rounded px-1 py-0.5">
              {pair}
            </span>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Step 1: Write the story -->
    {#if step === 1}
      <div>
        <label class="block text-sm md:text-base font-medium text-theme mb-1 md:mb-2" for="sentence">
          Write your story
        </label>
        <textarea
          id="sentence"
          bind:value={sentence}
          rows="4"
          placeholder="Write your story here with at least 5 words..."
          class="w-full rounded-lg border border-theme-muted/30 px-3 py-2 text-sm md:text-base bg-theme-surface focus:outline-none focus:ring-2 focus:ring-theme-accent/40 resize-none"
          style="color: var(--color-secondary);"
        ></textarea>
        <p class="text-xs text-theme-muted/60 mt-1">
          After writing your story, you'll select 5 words from it on the next step.
        </p>
      </div>

      <div class="flex gap-3 justify-end pt-1 md:pt-2">
        <button
          type="button"
          on:click={onCancel}
          class="min-h-[44px] md:min-h-[48px] px-5 md:px-6 text-sm md:text-base font-medium border rounded-lg hover:bg-theme-muted/5 transition-colors"
          style="color: var(--color-secondary); border-color: var(--color-border-muted);"
        >
          Cancel
        </button>
        <button
          type="button"
          on:click={goToStep2}
          class="min-h-[44px] md:min-h-[48px] px-5 md:px-6 text-sm md:text-base font-semibold rounded-lg hover:disabled:opacity-50 transition-colors"
          style="color: var(--color-dominant); background-color: var(--color-accent);"
        >
          Next: Select Words
        </button>
      </div>
    {/if}

    <!-- Step 2: Select 5 words -->
    {#if step === 2}
      <div>
        <p class="text-sm md:text-base font-medium text-theme mb-1 md:mb-2">
          Click on 5 words from your story
        </p>
        
        <!-- Display the story with clickable words -->
        <div class="rounded-lg border border-theme-muted/30 p-3 mb-3 bg-theme-surface">
          {#if words.length === 0}
            <p class="text-theme-muted/60 text-sm">No words found. Please write a story first.</p>
          {:else}
            {#each words as word, index}
              <button
                type="button"
                on:click={() => toggleWord(index)}
                class={wordClasses[index]}
              >
                {word}
              </button>
            {/each}
          {/if}
        </div>

        <!-- Show selected words count -->
        <div class="flex items-center gap-2 text-sm">
          <span class="text-theme-muted/60">Selected:</span>
          <span class="font-bold" style="color: var(--color-accent);">{selectedIndices.length}/5 words</span>
        </div>
      </div>

      <div class="flex gap-3 justify-end pt-1 md:pt-2">
        <button
          type="button"
          on:click={goBackToStep1}
          class="min-h-[44px] md:min-h-[48px] px-5 md:px-6 text-sm md:text-base font-medium border rounded-lg hover:bg-theme-muted/5 transition-colors"
          style="color: var(--color-secondary); border-color: var(--color-border-muted);"
        >
          Back
        </button>
        <button
          type="submit"
          disabled={saving || selectedIndices.length !== 5}
          class="min-h-[44px] md:min-h-[48px] px-5 md:px-6 text-sm md:text-base font-semibold rounded-lg hover:disabled:opacity-50 transition-colors disabled:opacity-50"
          style="color: var(--color-dominant); background-color: var(--color-accent);"
        >
          {saving ? 'Saving...' : isEdit ? 'Save changes' : 'Add story'}
        </button>
      </div>
    {/if}

    {#if error}
      <p class="text-sm md:text-base text-red-500">{error}</p>
    {/if}
  </form>
</div>
