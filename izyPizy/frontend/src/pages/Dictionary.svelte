<script>
  import { onMount } from 'svelte';
  import { getDictionary } from '../lib/api.js';
  import WordModal from '../components/WordModal.svelte';
  import Loader from '../components/Loader.svelte';

  let dictionary = {};
  let modalNumber = null;
  let isGridMode = true;
  let loading = true;

  async function loadDictionary() {
    loading = true;
    const data = await getDictionary();
    // data is an array of { number, words: [{id, word}] }
    const map = {};
    for (let i = 0; i < 100; i++) {
      const num = String(i).padStart(2, '0');
      map[num] = [];
    }
    for (const entry of data) {
      map[entry.number] = entry.words;
    }
    dictionary = map;
    loading = false;
  }

  async function refreshEntry(number) {
    const data = await getDictionary();
    const entry = data.find((e) => e.number === number);
    dictionary[number] = entry ? entry.words : [];
    // trigger reactivity
    dictionary = { ...dictionary };
  }

  onMount(loadDictionary);

  const pairs = Array.from({ length: 100 }, (_, i) => String(i).padStart(2, '0'));

  function openModal(num) {
    modalNumber = num;
  }

  function closeModal() {
    modalNumber = null;
  }
</script>

<div class="w-full p-4 pb-24 sm:p-6 md:p-8 lg:p-10">
  <div class="flex items-center justify-between mb-4 md:mb-6">
    <h1 class="text-2xl md:text-3xl font-bold text-[#4A4036]">Dictionary</h1>
    <button
      on:click={() => isGridMode = !isGridMode}
      class="px-3 py-1.5 text-sm font-medium text-[#C75B39] border border-[#C75B39]/30 rounded-lg hover:bg-[#C75B39]/5"
    >
      {isGridMode ? 'List' : 'Grid'}
    </button>
  </div>

  {#if loading}
    <Loader message="Loading dictionary..." />
  {:else if isGridMode}
    <!-- 10×10 grid -->
    <div class="grid grid-cols-10 gap-1 md:gap-2 text-center">
    {#each pairs as num}
      {@const words = dictionary[num] ?? []}
      {@const isEmpty = words.length === 0}
      <button
        class="flex flex-col items-center justify-center rounded-lg p-0.5 md:p-2 text-xs md:text-sm transition-colors
               {isEmpty
                 ? 'border border-dashed border-[#4A4036]/30 bg-[#F5F2EE] text-[#4A4036]/40 hover:bg-[#4A4036]/5'
                 : 'border border-[#C75B39]/20 bg-[#C75B39]/5 text-[#4A4036] hover:bg-[#C75B39]/10'}"
        style="min-height:2.5rem;"
        on:click={() => openModal(num)}
        aria-label="Edit words for {num}"
      >
        <span class="font-bold">{num}</span>
        {#if !isEmpty}
          <span class="mt-0.5 w-full truncate px-0.5 text-[#C75B39]" title={words[0].word}>
            {words[0].word}
          </span>
        {:else}
          <span class="mt-0.5 text-[#4A4036]/30">—</span>
        {/if}
      </button>
    {/each}
  </div>
  {:else}
    <!-- Linear list -->
    <div class="space-y-2">
      {#each pairs as num}
        {@const words = dictionary[num] ?? []}
        {@const isEmpty = words.length === 0}
        <button
          class="w-full flex items-center justify-between px-4 py-3 rounded-lg text-left transition-colors
                 {isEmpty
                   ? 'border border-dashed border-[#4A4036]/30 bg-[#F5F2EE] text-[#4A4036]/40'
                   : 'border border-[#4A4036]/20 bg-white text-[#4A4036] hover:bg-[#F5F2EE]'}"
          on:click={() => openModal(num)}
          aria-label="Edit words for {num}"
        >
          <span class="font-bold text-[#C75B39] w-12">{num}</span>
          <span class="flex-1 truncate">
            {#if !isEmpty}
              {words.map(w => w.word).join(', ')}
            {:else}
              <span class="text-[#4A4036]/30">—</span>
            {/if}
          </span>
          <span class="text-[#4A4036]/40 ml-2">→</span>
        </button>
      {/each}
</div>
    {:else}
    <!-- Linear list -->
    <div class="space-y-2">
    {#each pairs as num}
      {@const words = dictionary[num] ?? []}
      {@const isEmpty = words.length === 0}
      <button
        class="w-full flex items-center justify-between px-4 py-3 rounded-lg text-left transition-colors
               {isEmpty
                 ? 'border border-dashed border-[#4A4036]/30 bg-[#F5F2EE] text-[#4A4036]/40'
                 : 'border border-[#4A4036]/20 bg-white text-[#4A4036] hover:bg-[#4A4036]/5'}"
        on:click={() => openModal(num)}
        aria-label="Edit words for {num}"
      >
        <span class="font-bold text-[#C75B39] w-12">{num}</span>
        <span class="flex-1 truncate">
          {#if !isEmpty}
            {words.map(w => w.word).join(', ')}
          {:else}
            <span class="text-[#4A4036]/30">—</span>
          {/if}
        </span>
        <span class="text-[#4A4036]/40 ml-2">→</span>
      </button>
    {/each}
    </div>
    {/if}
</div>

{#if modalNumber !== null}
  <WordModal
    number={modalNumber}
    words={dictionary[modalNumber] ?? []}
    onClose={closeModal}
    onUpdate={refreshEntry}
  />
{/if}
