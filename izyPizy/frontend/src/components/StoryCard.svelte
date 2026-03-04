<script>
  /** @type {{ id: number, position: number, sentence?: string, word_0: string, word_1: string, word_2: string, word_3: string, word_4: string }} */
  export let story;

  /** @type {string} — 10-character pi digit string for this position */
  export let piDigits = '';

  /** @type {() => void} */
  export let onEdit = () => {};

  /** @type {() => void} */
  export let onDelete = () => {};

  $: words = [story.word_0, story.word_1, story.word_2, story.word_3, story.word_4];
  $: pairs = piDigits
    ? [0, 1, 2, 3, 4].map((i) => piDigits.slice(i * 2, i * 2 + 2))
    : ['??', '??', '??', '??', '??'];

  $: startDigit = story.position * 10 + 1;
  $: endDigit = story.position * 10 + 10;
</script>

<div class="rounded-2xl border border-gray-200 bg-white shadow-sm overflow-hidden">
  <!-- Header -->
  <div class="flex items-center justify-between bg-indigo-50 px-4 py-2">
    <span class="text-sm font-semibold text-indigo-700">
      Position {story.position}
    </span>
    <span class="text-xs text-indigo-400 font-mono">
      digits {startDigit}–{endDigit}:&nbsp;<span class="font-bold tracking-widest">{piDigits || '??????????'}</span>
    </span>
  </div>

  <!-- Words grid -->
  <div class="px-4 pt-3 pb-2">
    <div class="grid grid-cols-5 gap-1 text-center">
      {#each words as word, i}
        <div class="flex flex-col items-center gap-1">
          <span class="font-mono text-xs font-bold text-gray-400 bg-gray-100 rounded px-1 py-0.5 w-full text-center">
            {pairs[i]}
          </span>
          {#if word}
            <span class="text-sm font-medium text-gray-800 break-all leading-tight">{word}</span>
          {:else}
            <span class="text-sm text-gray-300 italic">—</span>
          {/if}
        </div>
      {/each}
    </div>

    {#if story.sentence}
      <p class="mt-3 text-sm text-gray-600 italic border-t border-gray-100 pt-2">
        "{story.sentence}"
      </p>
    {/if}
  </div>

  <!-- Actions -->
  <div class="flex justify-end gap-2 px-4 pb-3">
    <button
      on:click={onEdit}
      class="min-h-[44px] px-4 text-sm font-medium text-indigo-600 border border-indigo-200 rounded-lg hover:bg-indigo-50 transition-colors"
    >
      Edit
    </button>
    <button
      on:click={onDelete}
      class="min-h-[44px] px-4 text-sm font-medium text-red-500 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
    >
      Delete
    </button>
  </div>
</div>
