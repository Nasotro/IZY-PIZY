<script>
  /** @type {{ id: number, position: number, sentence?: string, word_0: string, word_1: string, word_2: string, word_3: string, word_4: string }} */
  export let story;

  /** @type {string} */
  export let piDigits = '';

  /** @type {() => void} */
  export let onEdit = () => {};

  /** @type {() => void} */
  export let onDelete = () => {};

  $: words = [story.word_0, story.word_1, story. word_2, story. word_3, story. word_4];
  $: pairs = piDigits
    ? [0, 1, 2, 3, 4].map((i) => piDigits. slice(i * 2, i * 2 + 2))
    : ['??', '??', '??', '??', '??'];

  $: startDigit = story. position * 10 + 1;
  $: endDigit = story. position * 10 + 10;

  $: highlightedSentence = getHighlightedSentence( story. sentence, words);

  function getHighlightedSentence( sentence, wordList) {
    if (!sentence) return null;
    const validWords = wordList. filter((w) => w);
    if (validWords. length === 0) return null;
    const parts = [];
    let remaining = sentence;
    while (remaining. length > 0) {
      let earliest = -1;
      let earliestMatch = null;
      let earliestWordIndex = -1;
      for (let i = 0; i < validWords. length; i++) {
        const word = validWords[i];
        const escaped = word. replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp( escaped, 'gi');
        const match = regex. exec(remaining);
        if (match && (earliest === -1 || match. index < earliest)) {
          earliest = match. index;
          earliestMatch = match[0];
          earliestWordIndex = i;
        }
      }
      if (earliest === -1) {
        parts. push({ text: remaining, highlight: false });
        break;
      }
      if (earliest > 0) {
        parts. push({ text: remaining. slice(0, earliest), highlight: false });
      }
      parts. push({ text: earliestMatch, highlight: true, wordIndex: earliestWordIndex });
      remaining = remaining. slice(earliest + earliestMatch. length);
    }
    return parts;
  }
</script>
<div class="rounded-2xl border border-gray-200 bg-white shadow-sm overflow-hidden max-w-full">
  <div class="px-4 py-3 md:px-6 md:py-4">
    <p class="text-xs text-gray-400 font- medium mb-1">{startDigit} - {endDigit}</p>

    {#if story. sentence && highlightedSentence}
      <p class="text-xl md:text-2xl lg:text-3xl text-gray-700 leading-snug">
        "{#each highlightedSentence as part}{#if part. highlight}<span class="group relative inline-block cursor-default no-underline"><span class="relative font-medium text-gray-900">{part. text}</span><span class="absolute bottom-0 left-0 w- full h-0.5 bg-gradient- to-r from-amber-400 to-amber-500 rounded- full scale-x-0 group- hover:scale-x-100 transition-transform duration-300 origin-left"></span><span class="absolute -top-7 left-1/2 -translate-x-1/2 px-2 py-1 text-sm font-bold text-white bg-amber-500 rounded-lg shadow-xl opacity-0 group- hover:opacity-100 transition-opacity duration-200 pointer- events-none whitespace-nowrap z-20">{pairs[part. wordIndex]}</span></span>{:else}{part. text}{/if}{/each}"
      </p>
    {:else if story. sentence}
      <p class="text-xl md:text-2xl lg:text-3xl text-gray-700 italic leading-snug">"{story. sentence}"</p>
    {:else}
      <p class="text-lg md:text-xl text-gray-300 italic">No sentence</p>
    {/if}
  </div>

  <div class="flex justify-end gap-2 px-4 pb-3 md:px-6 md:pb-4">
    <button
      on:click={onEdit}
      class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-medium text-indigo-600 border border-indigo-200 rounded-lg hover:bg-indigo-50 transition-colors"
    >
      Edit
    </button>
    <button
      on:click={onDelete}
      class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-medium text-red-500 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
    >
      Delete
    </button>
  </div>
</div>