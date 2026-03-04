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

  // All past digits from 0 to currentPosition
  let allDigits = '';

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
    if (pos <= 0) { allDigits = ''; return; }
    try {
      const data = await getPi(0, pos);
      allDigits = data.digits;
    } catch {
      allDigits = '';
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

  // Group all past digits into lines of 5 pairs (10 digits)
  // Each line = array of pairs (2-char strings), last pair may be incomplete
  /** @type {Array<Array<string>>} */
  $: digitLines = (() => {
    const lines = [];
    for (let i = 0; i < allDigits.length; i += 10) {
      const chunk = allDigits.slice(i, i + 10);
      const pairs = [];
      for (let j = 0; j < chunk.length; j += 2) {
        pairs.push(chunk.slice(j, j + 2));
      }
      lines.push(pairs);
    }
    return lines;
  })();

  // Determine where the cursor "_" goes: which line and after which pair
  $: cursorLineIndex = Math.floor(currentPosition / 10);
  $: cursorInLinePos = currentPosition % 10; // 0-9 digit offset within that line

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

  <!-- Context: all past digits grouped by pairs, 5 pairs per line -->
  <div class="w-full space-y-1 overflow-y-auto max-h-40 rounded-xl bg-gray-50 px-3 py-2">
    {#each digitLines as pairs, lineIdx}
      <div class="flex gap-2 justify-center font-mono text-lg leading-tight">
        {#each pairs as pair}
          <span class="text-gray-400 tracking-widest">{pair}</span>
        {/each}
        {#if lineIdx === cursorLineIndex && pairs.length < 5}
          <span class="text-indigo-400 animate-pulse">_</span>
        {/if}
      </div>
    {/each}
    {#if digitLines.length === 0 || (digitLines.length > 0 && digitLines[digitLines.length - 1].length === 5 && cursorLineIndex >= digitLines.length)}
      <div class="flex gap-2 justify-center font-mono text-lg leading-tight">
        <span class="text-indigo-400 animate-pulse">_</span>
      </div>
    {/if}
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
