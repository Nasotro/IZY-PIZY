<script>
  export let story;
  export let piDigits = '';
  export let showFull = true;
  export let onEdit = () => {};
  export let onDelete = () => {};

  $: words = [story.word_0, story.word_1, story.word_2, story.word_3, story.word_4];
  $: pairs = piDigits
    ? [0, 1, 2, 3, 4].map((i) => piDigits.slice(i * 2, i * 2 + 2))
    : ['??', '??', '??', '??', '??'];

  $: startDigit = story.position * 10 + 1;
  $: endDigit = story.position * 10 + 10;

  $: highlightedSentence = getHighlightedSentence(story.sentence, words);

  function getHighlightedSentence(sentence, wordList) {
    if (!sentence) return null;
    const validWords = wordList.filter((w) => w);
    if (validWords.length === 0) return null;
    const parts = [];
    let remaining = sentence;
    while (remaining.length > 0) {
      let earliest = -1;
      let earliestMatch = null;
      let earliestWordIndex = -1;
      for (let i = 0; i < validWords.length; i++) {
        const word = validWords[i];
        const escaped = word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const regex = new RegExp(escaped, 'gi');
        const match = regex.exec(remaining);
        if (match && (earliest === -1 || match.index < earliest)) {
          earliest = match.index;
          earliestMatch = match[0];
          earliestWordIndex = i;
        }
      }
      if (earliest === -1) {
        parts.push({ text: remaining, highlight: false });
        break;
      }
      if (earliest > 0) {
        parts.push({ text: remaining.slice(0, earliest), highlight: false });
      }
      parts.push({ text: earliestMatch, highlight: true, wordIndex: earliestWordIndex });
      remaining = remaining.slice(earliest + earliestMatch.length);
    }
    return parts;
  }
</script>
<div class="rounded-2xl border border-theme-muted/10 bg-theme-surface shadow-sm overflow-hidden max-w-full">
  <div class="px-4 py-3 md:px-6 md:py-4">
    {#if showFull}
      <p class="text-xs text-theme-muted/40 font-medium mb-1">{startDigit} - {endDigit}</p>
    {/if}

    {#if story.sentence && highlightedSentence}
      <p class="text-xl md:text-2xl lg:text-3xl text-theme leading-snug">
        "{#each highlightedSentence as part}{#if part.highlight}<span class="group relative inline-block cursor-default"><span class="relative font-semibold text-theme group-hover:scale-105 group-hover:text-theme-accent transition-all duration-200 border-b-2 border-theme-accent/50 group-hover:border-theme-accent">{part.text}</span><span class="absolute -top-7 left-1/2 -translate-x-1/2 px-2 py-1 text-sm font-bold rounded-lg shadow-xl opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-20" style="color: var(--color-dominant); background-color: var(--color-accent);">{pairs[part.wordIndex]}</span></span>{:else}{part.text}{/if}{/each}"
      </p>
    {:else if story.sentence}
      <p class="text-xl md:text-2xl lg:text-3xl text-theme italic leading-snug">"{story.sentence}"</p>
    {:else}
      <p class="text-lg md:text-xl text-theme-muted/30 italic">No sentence</p>
    {/if}
  </div>

  <div class="flex justify-end gap-2 px-4 pb-3 md:px-6 md:pb-4">
    <button on:click={onEdit} class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-medium border rounded-lg hover:bg-theme-accent/5 transition-colors" style="color: var(--color-accent); border-color: var(--color-accent);">Edit</button>
    <button on:click={onDelete} class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-medium border rounded-lg hover:bg-red-50 transition-colors" style="color: var(--color-accent); border-color: var(--color-border-muted);">Delete</button>
  </div>
</div>