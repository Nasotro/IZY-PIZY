<script>
  import { onMount, tick } from 'svelte';
  import { verifyDigit, getPi } from '../lib/api.js';

  const LS_KEY = 'izipizy_position';

  let currentPosition = 0;
  /** @type {'correct' | 'wrong' | null} */
  let lastResult = null;
  let expectedDigit = '';
  let inputEl;
  let inputValue = '';
  let busy = false;

  // Context: last 5 + 1 upcoming digits fetched from API
  let contextDigits = ''; // string of up to 6 chars (5 past + current slot)
  let contextStart = 0;

  // Jump popover
  let jumpOpen = false;
  let jumpValue = '';

  // Flash timeout handle
  let flashTimer;

  function loadPosition() {
    const stored = localStorage.getItem(LS_KEY);
    currentPosition = stored !== null ? parseInt(stored, 10) : 0;
  }

  function savePosition(pos) {
    localStorage.setItem(LS_KEY, String(pos));
  }

  async function fetchContext(pos) {
    const start = Math.max(0, pos - 5);
    const length = 6; // 5 past + current position slot
    try {
      const data = await getPi(start, length);
      contextDigits = data.digits;
      contextStart = start;
    } catch {
      contextDigits = '';
    }
  }

  async function handleInput(e) {
    if (busy) { inputValue = ''; return; }
    const raw = inputValue;
    inputValue = '';
    if (!raw) return;

    const digit = raw[raw.length - 1]; // last typed char (in case IME batched)
    if (!/^[0-9]$/.test(digit)) return;

    busy = true;
    clearTimeout(flashTimer);
    lastResult = null;

    try {
      const data = await verifyDigit(currentPosition, digit);
      if (data.correct) {
        lastResult = 'correct';
        expectedDigit = '';
        currentPosition += 1;
        savePosition(currentPosition);
        await fetchContext(currentPosition);
        flashTimer = setTimeout(() => { lastResult = null; }, 600);
      } else {
        lastResult = 'wrong';
        expectedDigit = data.expected ?? '';
        flashTimer = setTimeout(() => { lastResult = null; }, 1200);
      }
    } catch (err) {
      lastResult = null;
    } finally {
      busy = false;
      await tick();
      inputEl?.focus();
    }
  }

  function reset() {
    currentPosition = 0;
    savePosition(0);
    lastResult = null;
    expectedDigit = '';
    inputValue = '';
    fetchContext(0);
    tick().then(() => inputEl?.focus());
  }

  function openJump() {
    jumpOpen = true;
    jumpValue = String(currentPosition);
  }

  function confirmJump() {
    const n = parseInt(jumpValue, 10);
    if (!isNaN(n) && n >= 0) {
      currentPosition = n;
      savePosition(n);
      lastResult = null;
      expectedDigit = '';
      fetchContext(n);
    }
    jumpOpen = false;
    tick().then(() => inputEl?.focus());
  }

  function cancelJump() {
    jumpOpen = false;
    tick().then(() => inputEl?.focus());
  }

  // Derive context display: up to 5 past digits + a placeholder for current slot
  $: pastStart = Math.max(0, currentPosition - 5);
  $: pastDigits = contextDigits.slice(
    pastStart - contextStart,
    currentPosition - contextStart
  );

  onMount(() => {
    loadPosition();
    fetchContext(currentPosition);
    tick().then(() => inputEl?.focus());
  });
</script>

<div class="max-w-sm mx-auto px-4 py-8 flex flex-col items-center gap-6">
  <!-- Title -->
  <h1 class="text-2xl font-bold text-gray-800 self-start">🧠 Training</h1>

  <!-- Position counter -->
  <div class="w-full text-center">
    <span class="text-sm text-gray-500">Position</span>
    <p class="text-5xl font-mono font-bold text-indigo-700 leading-none mt-1">
      {currentPosition}
    </p>
  </div>

  <!-- Context: last 5 correct digits -->
  <div class="flex items-end gap-1 h-10">
    {#each pastDigits.split('') as d}
      <span class="font-mono text-2xl text-gray-300 leading-none">{d}</span>
    {/each}
    <span class="font-mono text-2xl text-gray-200 leading-none">_</span>
  </div>

  <!-- Big input -->
  <div class="relative w-40 h-40">
    <input
      bind:this={inputEl}
      bind:value={inputValue}
      on:input={handleInput}
      inputmode="numeric"
      maxlength="2"
      autocomplete="off"
      spellcheck="false"
      aria-label="Enter the next digit of pi"
      class="w-full h-full rounded-3xl border-4 text-center text-6xl font-mono font-bold outline-none transition-colors duration-150
        {lastResult === 'correct'
          ? 'border-green-400 bg-green-50 text-green-600'
          : lastResult === 'wrong'
          ? 'border-red-400 bg-red-50 text-red-500'
          : 'border-indigo-300 bg-white text-gray-800 focus:border-indigo-500'}"
    />
  </div>

  <!-- Feedback message -->
  <div class="h-8 text-center">
    {#if lastResult === 'correct'}
      <p class="text-green-600 font-semibold text-lg animate-pulse">✓ Correct!</p>
    {:else if lastResult === 'wrong'}
      <p class="text-red-500 font-semibold text-lg">
        ✗ Wrong! Expected: <span class="font-mono">{expectedDigit}</span>
      </p>
    {/if}
  </div>

  <!-- Controls -->
  <div class="flex gap-3 w-full justify-center">
    <button
      on:click={reset}
      class="min-h-[44px] px-6 text-sm font-medium text-gray-600 border border-gray-300 rounded-xl hover:bg-gray-100 transition-colors"
    >
      Reset
    </button>
    <button
      on:click={openJump}
      class="min-h-[44px] px-6 text-sm font-medium text-indigo-600 border border-indigo-200 rounded-xl hover:bg-indigo-50 transition-colors"
    >
      Jump to…
    </button>
  </div>

  <!-- Jump popover -->
  {#if jumpOpen}
    <div class="w-full rounded-2xl border border-indigo-200 bg-indigo-50 p-5 shadow space-y-3">
      <label class="block text-sm font-medium text-gray-700" for="jump-input">
        Jump to position (0–999)
      </label>
      <input
        id="jump-input"
        type="number"
        min="0"
        max="999"
        bind:value={jumpValue}
        on:keydown={(e) => { if (e.key === 'Enter') confirmJump(); if (e.key === 'Escape') cancelJump(); }}
        class="w-full min-h-[44px] rounded-lg border border-gray-300 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />
      <div class="flex gap-3 justify-end">
        <button
          on:click={cancelJump}
          class="min-h-[44px] px-4 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-100"
        >
          Cancel
        </button>
        <button
          on:click={confirmJump}
          class="min-h-[44px] px-4 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700"
        >
          Go
        </button>
      </div>
    </div>
  {/if}
</div>
