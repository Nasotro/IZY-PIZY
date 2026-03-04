<script>
  import { onMount } from 'svelte';
  import { getDictionary } from '../lib/api.js';
  import WordModal from '../components/WordModal.svelte';

  // dictionary[number] = [ { id, word }, ... ]
  let dictionary = {};
  let modalNumber = null;

  async function loadDictionary() {
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

<div class="p-4 pb-24 sm:p-6">
  <h1 class="mb-4 text-2xl font-bold text-gray-800">Dictionary</h1>

  <!-- 10×10 grid -->
  <div class="grid grid-cols-10 gap-1 text-center">
    {#each pairs as num}
      {@const words = dictionary[num] ?? []}
      {@const isEmpty = words.length === 0}
      <button
        class="flex flex-col items-center justify-center rounded-lg p-1 text-xs transition-colors
               {isEmpty
                 ? 'border border-dashed border-gray-300 bg-gray-50 text-gray-400 hover:bg-gray-100'
                 : 'border border-indigo-200 bg-indigo-50 text-indigo-800 hover:bg-indigo-100'}"
        style="min-height:3.5rem;"
        on:click={() => openModal(num)}
        aria-label="Edit words for {num}"
      >
        <span class="font-bold">{num}</span>
        {#if !isEmpty}
          <span class="mt-0.5 w-full truncate px-0.5 text-indigo-600" title={words[0].word}>
            {words[0].word}
          </span>
        {:else}
          <span class="mt-0.5 text-gray-300">—</span>
        {/if}
      </button>
    {/each}
  </div>
</div>

{#if modalNumber !== null}
  <WordModal
    number={modalNumber}
    words={dictionary[modalNumber] ?? []}
    onClose={closeModal}
    onUpdate={refreshEntry}
  />
{/if}
