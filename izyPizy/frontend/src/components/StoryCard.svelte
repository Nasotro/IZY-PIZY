<script>
  export let story;
  export let piDigits = '';
  export let showFull = true;
  export let onEdit = () => {};
  export let onDelete = () => {};
  export let onGenerateImage = () => {};
  export let onOpenImageGeneration = () => {};
  export let generatingImage = false;
  export let hasImageGenerationModal = false;

  $: words = [story.word_0, story.word_1, story.word_2, story.word_3, story.word_4];
  $: pairs = piDigits
    ? [0, 1, 2, 3, 4].map((i) => piDigits.slice(i * 2, i * 2 + 2))
    : ['??', '??', '??', '??', '??'];

  $: startDigit = story.position * 10 + 1;
  $: endDigit = story.position * 10 + 10;

  $: highlightedSentence = getHighlightedSentence(story.sentence, words);
  
  $: imageSrc = story.image_url;
  $: canGenerateImage = !!story.sentence;

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

<div class="rounded-lg border-2 bg-theme-surface shadow-retro overflow-hidden max-w-full" style="border-color: var(--color-border);">
  {#if showFull}
    <div class="px-4 py-2 md:px-6 border-b" style="border-color: var(--color-border);">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <div class="flex flex-wrap gap-2">
          {#each pairs as pair}
            <span class="text-base md:text-lg font-mono font-bold" style="color: var(--color-accent);">{pair}</span>
          {/each}
        </div>
        <span class="text-sm font-mono" style="color: var(--color-muted);">{startDigit} - {endDigit}</span>
      </div>
    </div>
  {/if}

  <div class="px-4 py-3 md:px-6 md:py-4">

    {#if imageSrc}
      <div class="mb-4 flex justify-center">
        <div class="relative inline-block border-2 shadow-retro-sm" style="border-color: var(--color-border); background-color: var(--color-bg-tertiary); padding: 6px;">
          <span class="absolute -top-2.5 left-6 h-6 w-16 -rotate-6 opacity-85" style="background-color: #F4A261; border: 1px solid var(--color-border);"></span>
          <img 
            src={imageSrc} 
            alt="Story illustration"
            class="max-w-full max-h-48 md:max-h-64 object-contain"
          />
        </div>
      </div>
    {/if}

    {#if story.sentence && highlightedSentence}
      <p class="text-xl md:text-2xl lg:text-3xl leading-snug" style="color: var(--color-secondary);">
        {#each highlightedSentence as part}{#if part.highlight}<span class="group relative inline-block cursor-default"><span class="relative font-bold px-1 transition-colors duration-150 group-hover:bg-accentHover" style="background-color: var(--color-accent); color: var(--color-bg-tertiary);">{part.text}</span><span class="absolute -top-7 left-1/2 -translate-x-1/2 px-2 py-1 font-mono text-sm font-bold border-2 shadow-retro-sm opacity-0 group-hover:opacity-100 transition-opacity duration-150 pointer-events-none whitespace-nowrap z-20" style="color: var(--color-bg-tertiary); background-color: var(--color-secondary); border-color: var(--color-border);">{pairs[part.wordIndex]}</span></span>{:else}{part.text}{/if}{/each}
      </p>
    {:else if story.sentence}
      <p class="text-xl md:text-2xl lg:text-3xl italic leading-snug" style="color: var(--color-secondary);">{story.sentence}</p>
    {:else}
      <p class="text-lg md:text-xl italic" style="color: var(--color-muted); opacity: 0.6;">No sentence</p>
    {/if}
  </div>

  {#if showFull}
    <div class="hidden lg:block px-6 pb-4">
      <div class="flex justify-end">
        <div class="flex gap-2">
          {#if canGenerateImage && !imageSrc}
            {#if hasImageGenerationModal}
              <button 
                on:click={onOpenImageGeneration} 
                disabled={generatingImage}
                class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-mono font-bold uppercase tracking-wider btn-retro btn-retro-secondary disabled:opacity-50"
              >
                {generatingImage ? 'Generating...' : 'Generate Image'}
              </button>
            {:else}
              <button 
                on:click={onGenerateImage} 
                disabled={generatingImage}
                class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-mono font-bold uppercase tracking-wider btn-retro btn-retro-secondary disabled:opacity-50"
              >
                {generatingImage ? 'Generating...' : 'Generate Image'}
              </button>
            {/if}
          {:else if imageSrc}
            <span class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-mono font-bold uppercase tracking-wider rounded-lg border-2 flex items-center" style="color: var(--color-muted); border-color: var(--color-border); background-color: var(--color-surface-alt);">
              Image generated
            </span>
          {/if}
          <button on:click={onEdit} class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-mono font-bold uppercase tracking-wider btn-retro btn-retro-secondary">Edit</button>
          <button on:click={onDelete} class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-mono font-bold uppercase tracking-wider btn-retro btn-retro-secondary">Delete</button>
        </div>
      </div>
    </div>
  {/if}

  <div class="flex justify-end gap-2 px-4 pb-3 md:px-6 md:pb-4 lg:hidden">
    {#if canGenerateImage && !imageSrc}
      {#if hasImageGenerationModal}
        <button 
          on:click={onOpenImageGeneration} 
          disabled={generatingImage}
          class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-medium rounded-lg border hover:bg-theme-accent/5 transition-colors disabled:opacity-50"
          style="color: var(--color-accent); border-color: var(--color-accent);"
        >
          {generatingImage ? 'Generating...' : 'Generate Image'}
        </button>
      {:else}
        <button 
          on:click={onGenerateImage} 
          disabled={generatingImage}
          class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-medium rounded-lg border hover:bg-theme-accent/5 transition-colors disabled:opacity-50"
          style="color: var(--color-accent); border-color: var(--color-accent);"
        >
          {generatingImage ? 'Generating...' : 'Generate Image'}
        </button>
      {/if}
    {:else if imageSrc}
      <span class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-medium rounded-lg text-theme-muted/60 bg-theme-surface-alt">
        Image generated
      </span>
    {/if}
    <button on:click={onEdit} class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-medium border rounded-lg hover:bg-theme-accent/5 transition-colors" style="color: var(--color-accent); border-color: var(--color-accent);">Edit</button>
    <button on:click={onDelete} class="min-h-[40px] md:min-h-[44px] px-4 md:px-5 text-sm md:text-base font-medium border rounded-lg hover:bg-red-50 transition-colors" style="color: var(--color-accent); border-color: var(--color-border-muted);">Delete</button>
  </div>
</div>