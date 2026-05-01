<script>
  import { onMount, tick } from 'svelte';
  import { verifyDigit, getPi } from '../lib/api.js';
  import Loader from '../components/Loader.svelte';

  const LS_KEY = 'izipizy_position';
  const LS_SETTINGS_KEY = 'izipizy_training_settings';

  let currentPosition = 0;
  /** @type {'correct' | 'wrong' | null} */
  let lastResult = null;
  let expectedDigit = '';
  let inputEl;
  let inputValue = '';
  let inputQueue = Promise.resolve();
  let digitsContainer;

  // All past digits from 0 to currentPosition
  let allDigits = '';
  let displayDigits = '';

  // Jump popover
  let jumpOpen = false;
  let jumpValue = '';

  // Flash timeout handle
  let flashTimer;

  // Settings
  let settingsOpen = false;
  let settings = {
    jumpEnabled: true,
    timerMode: false,
    errorMode: false
  };

  // Timer
  let timerRunning = false;
  let startTime = 0;
  let elapsedTime = 0;
  let timerInterval;
  let sessionStartTime = null;

  // Error mode state
  let errorStopped = false;

  // Loading state
  let loadingContext = false;

  function loadSettings() {
    const stored = localStorage.getItem(LS_SETTINGS_KEY);
    if (stored) {
      try {
        settings = { ...settings, ...JSON.parse(stored) };
      } catch {}
    }
  }

  function saveSettings() {
    localStorage.setItem(LS_SETTINGS_KEY, JSON.stringify(settings));
  }

  function startTimer() {
    if (!timerRunning && settings.timerMode) {
      timerRunning = true;
      startTime = Date.now();
      sessionStartTime = sessionStartTime || Date.now();
      timerInterval = setInterval(() => {
        elapsedTime = Math.floor((Date.now() - startTime) / 1000);
      }, 1000);
    }
  }

  function stopTimer() {
    if (timerRunning) {
      timerRunning = false;
      clearInterval(timerInterval);
    }
  }

  function resetTimer() {
    stopTimer();
    elapsedTime = 0;
    startTime = 0;
    sessionStartTime = null;
  }

  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  function saveResult() {
    if (settings.timerMode && sessionStartTime) {
      const results = JSON.parse(localStorage.getItem('izipizy_results') || '[]');
      results.push({
        position: currentPosition,
        date: new Date().toISOString(),
        duration: elapsedTime
      });
      localStorage.setItem('izipizy_results', JSON.stringify(results));
    }
  }

  function loadPosition() {
    const stored = localStorage.getItem(LS_KEY);
    currentPosition = stored !== null ? parseInt(stored, 10) : 0;
  }

  function savePosition(pos) {
    localStorage.setItem(LS_KEY, String(pos));
  }

  async function fetchContext(pos) {
    if (pos <= 0) { allDigits = ''; return; }
    loadingContext = true;
    try {
      const data = await getPi(0, pos);
      allDigits = data.digits;
    } catch {
      allDigits = '';
    } finally {
      loadingContext = false;
    }
    tick().then(() => {
      if (digitsContainer) digitsContainer.scrollTop = digitsContainer.scrollHeight;
    });
  }

  async function handleInput(e) {
    const raw = inputValue;
    inputValue = '';
    if (!raw) return;

    const digit = raw[raw.length - 1];
    if (!/^[0-9]$/.test(digit)) return;

    startTimer();

    inputQueue = inputQueue.then(async () => {
      const pos = currentPosition;
      try {
        const data = await verifyDigit(pos, digit);
        clearTimeout(flashTimer);
        lastResult = null;

        if (data.correct) {
          lastResult = 'correct';
          expectedDigit = '';
          currentPosition += 1;
          savePosition(currentPosition);
          displayDigits += digit;
          tick().then(() => {
            if (digitsContainer) digitsContainer.scrollTop = digitsContainer.scrollHeight;
          });
          flashTimer = setTimeout(() => { lastResult = null; }, 600);
        } else {
          lastResult = 'wrong';
          expectedDigit = data.expected ?? '';
          flashTimer = setTimeout(() => { lastResult = null }, 1200);

          if (settings.errorMode) {
            stopTimer();
            saveResult();
            errorStopped = true;
          }
        }
      } catch (err) {
        lastResult = null;
      }
      tick().then(() => inputEl?.focus());
    });
  }

  async function reset() {
    currentPosition = 0;
    savePosition(0);
    lastResult = null;
    expectedDigit = '';
    inputValue = '';
    displayDigits = '';
    errorStopped = false;
    resetTimer();
    if (currentPosition > 0) {
      await fetchContext(0);
      displayDigits = allDigits;
    }
    tick().then(() => inputEl?.focus());
  }

  function openJump() {
    jumpOpen = true;
    jumpValue = String(currentPosition);
  }

  async function confirmJump() {
    const n = parseInt(jumpValue, 10);
    if (!isNaN(n) && n >= 0) {
      currentPosition = n;
      savePosition(n);
      lastResult = null;
      expectedDigit = '';
      displayDigits = '';
      await fetchContext(n);
      displayDigits = allDigits;
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
    for (let i = 0; i < displayDigits.length; i += 10) {
      const chunk = displayDigits.slice(i, i + 10);
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

  onMount(async () => {
    loadSettings();
    loadPosition();
    if (currentPosition > 0) {
      await fetchContext(currentPosition);
      displayDigits = allDigits;
    }
    tick().then(() => inputEl?.focus());
  });
</script>

<div class="w-full mx-auto px-4 py-6 md:py-10 lg:py-12 flex flex-col items-center gap-5 md:gap-8">
  <!-- Title -->
  <h1 class="text-2xl md:text-3xl font-bold text-[#4A4036] self-start">🧠 Training</h1>

  <!-- Position counter -->
  <div class="w-full text-center">
    <span class="text-sm md:text-base text-gray-500">Position</span>
    <p class="text-5xl md:text-6xl lg:text-7xl font-mono font-bold text-[#C75B39] leading-none mt-1">
      {currentPosition}
    </p>
    {#if settings.timerMode}
      <p class="text-2xl md:text-3xl font-mono font-bold text-[#4A4036] mt-2">
        {formatTime(elapsedTime)}
      </p>
    {/if}
  </div>

  <!-- Context: all past digits grouped by pairs, 5 pairs per line -->
  <div bind:this={digitsContainer} class="w-full space-y-1 overflow-y-auto max-h-40 md:max-h-48 lg:max-h-56 rounded-xl bg-[#F5F2EE] px-3 py-2 md:px-4 md:py-3">
    {#if loadingContext}
      <div class="flex items-center justify-center py-4">
        <Loader size="sm" message="Loading digits..." />
      </div>
    {:else}
    {#each digitLines as pairs, lineIdx}
      <div class="flex gap-2 md:gap-3 justify-center font-mono text-lg md:text-xl lg:text-2xl leading-tight">
        {#each pairs as pair}
          <span class="text-[#4A4036]/40 tracking-widest">{pair}</span>
        {/each}
        {#if lineIdx === cursorLineIndex && pairs.length < 5}
          <span class="text-[#C75B39]/60 animate-pulse">_</span>
        {/if}
      </div>
    {/each}
    {#if digitLines.length === 0 || (digitLines.length > 0 && digitLines[digitLines.length - 1].length === 5 && cursorLineIndex >= digitLines.length)}
      <div class="flex gap-2 md:gap-3 justify-center font-mono text-lg md:text-xl lg:text-2xl leading-tight">
        <span class="text-[#C75B39]/60 animate-pulse">_</span>
      </div>
    {/if}
    {/if}
  </div>

  <!-- Big input -->
  <div class="relative w-48 h-48 md:w-56 md:h-56 lg:w-64 lg:h-64">
    <input
      bind:this={inputEl}
      bind:value={inputValue}
      on:input={handleInput}
      inputmode="numeric"
      maxlength="2"
      autocomplete="off"
      spellcheck="false"
      disabled={errorStopped}
      aria-label="Enter the next digit of pi"
      class="w-full h-full rounded-3xl border-4 text-center text-6xl md:text-7xl lg:text-8xl font-mono font-bold outline-none transition-colors duration-150
        {errorStopped
          ? 'border-red-300 bg-red-50 text-red-400'
          : lastResult === 'correct'
          ? 'border-green-400 bg-green-50 text-green-600'
          : lastResult === 'wrong'
          ? 'border-red-400 bg-red-50 text-red-500'
          : 'border-[#C75B39]/30 bg-[#FEFCF9] text-[#4A4036] focus:border-[#C75B39]'}"
    />
  </div>

  <!-- Feedback message -->
  <div class="h-8 md:h-10 text-center">
    {#if errorStopped}
      <p class="text-red-600 font-bold text-xl md:text-2xl">Game Over!</p>
    {:else if lastResult === 'correct'}
      <p class="w-full text-center text-lg md:text-xl font-semibold text-green-600 animate-pulse">✓ Correct!</p>
    {:else if lastResult === 'wrong'}
      <p class="w-full text-center text-lg md:text-xl font-semibold text-red-500">
        ✗ Wrong! Expected: <span class="font-mono">{expectedDigit}</span>
      </p>
    {/if}
  </div>

  <!-- Controls -->
  {#if errorStopped}
    <div class="flex flex-col items-center gap-4 w-full">
      <p class="text-[#4A4036] text-base md:text-lg">You reached position <span class="font-bold text-[#C75B39]">{currentPosition}</span></p>
      <button
        on:click={reset}
        class="min-h-[44px] md:min-h-[48px] px-8 md:px-10 text-base md:text-lg font-semibold text-[#FEFCF9] bg-[#C75B39] rounded-xl hover:bg-[#A84829] transition-colors"
      >
        🔄 Restart
      </button>
    </div>
  {:else}
    <div class="flex gap-3 w-full justify-center flex-wrap">
      <button
        on:click={reset}
        class="min-h-[44px] md:min-h-[48px] px-6 md:px-8 text-sm md:text-base font-medium text-[#4A4036] border border-[#4A4036]/30 rounded-xl hover:bg-[#4A4036]/5 transition-colors"
      >
        Reset
      </button>
      {#if settings.jumpEnabled}
        <button
          on:click={openJump}
          class="min-h-[44px] md:min-h-[48px] px-6 md:px-8 text-sm md:text-base font-medium text-[#C75B39] border border-[#C75B39]/30 rounded-xl hover:bg-[#C75B39]/5 transition-colors"
        >
          Jump to…
        </button>
      {/if}
      <button
        on:click={() => { settingsOpen = !settingsOpen; }}
        class="min-h-[44px] md:min-h-[48px] px-6 md:px-8 text-sm md:text-base font-medium text-[#4A4036] border border-[#4A4036]/30 rounded-xl hover:bg-[#4A4036]/5 transition-colors"
      >
        ⚙️ Settings
      </button>
    </div>
  {/if}

  <!-- Jump popover -->
  {#if jumpOpen}
    <div class="w-full rounded-2xl border border-[#C75B39]/20 bg-[#F5F2EE] p-5 md:p-6 shadow space-y-3">
      <label class="block text-sm md:text-base font-medium text-[#4A4036]" for="jump-input">
        Jump to position (0–999)
      </label>
      <input
        id="jump-input"
        type="number"
        min="0"
        max="999"
        bind:value={jumpValue}
        on:keydown={(e) => { if (e.key === 'Enter') confirmJump(); if (e.key === 'Escape') cancelJump(); }}
        class="w-full min-h-[44px] md:min-h-[48px] rounded-lg border border-[#4A4036]/30 px-3 text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-[#C75B39]/40"
      />
      <div class="flex gap-3 justify-end">
        <button
          on:click={cancelJump}
          class="min-h-[44px] md:min-h-[48px] px-4 md:px-5 text-sm md:text-base text-[#4A4036] border border-[#4A4036]/30 rounded-lg hover:bg-[#4A4036]/5"
        >
          Cancel
        </button>
        <button
          on:click={confirmJump}
          class="min-h-[44px] md:min-h-[48px] px-4 md:px-5 text-sm md:text-base font-semibold text-[#FEFCF9] bg-[#C75B39] rounded-lg hover:bg-[#A84829]"
        >
          Go
        </button>
      </div>
    </div>
  {/if}

  <!-- Settings panel modal -->
  {#if settingsOpen}
    <div
      class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4"
      on:click|self={() => settingsOpen = false}
      on:keydown={(e) => { if (e.key === 'Escape') settingsOpen = false; }}
      role="dialog"
      aria-modal="true"
      tabindex="-1"
    >
      <div class="w-full max-w-md rounded-2xl border border-[#4A4036]/30 bg-[#FEFCF9] p-6 md:p-8 shadow-2xl space-y-6">
        <div class="flex items-center justify-between">
          <h2 class="text-xl md:text-2xl font-bold text-[#4A4036]">Training Settings</h2>
          <button
            on:click={() => settingsOpen = false}
            class="text-[#4A4036]/60 hover:text-[#4A4036] text-2xl leading-none"
          >
            ×
          </button>
        </div>

        <div class="space-y-4">
          <label class="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              bind:checked={settings.jumpEnabled}
              on:change={saveSettings}
              class="w-5 h-5 text-[#C75B39] rounded focus:ring-[#C75B39] bg-[#F5F2EE] border-[#4A4036]/30"
            />
            <span class="text-base text-[#4A4036]">Enable "Jump to" button</span>
          </label>

          <label class="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              bind:checked={settings.timerMode}
              on:change={saveSettings}
              class="w-5 h-5 text-[#C75B39] rounded focus:ring-[#C75B39] bg-[#F5F2EE] border-[#4A4036]/30"
            />
            <span class="text-base text-[#4A4036]">Timer mode (show timer & store results)</span>
          </label>

          <label class="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              bind:checked={settings.errorMode}
              on:change={saveSettings}
              class="w-5 h-5 text-[#C75B39] rounded focus:ring-[#C75B39] bg-[#F5F2EE] border-[#4A4036]/30"
            />
            <span class="text-base text-[#4A4036]">Error mode (reset on wrong answer)</span>
          </label>
        </div>

        <button
          on:click={() => settingsOpen = false}
          class="w-full min-h-[44px] md:min-h-[48px] text-base font-semibold text-[#FEFCF9] bg-[#C75B39] rounded-xl hover:bg-[#A84829] transition-colors"
        >
          Done
        </button>
      </div>
    </div>
  {/if}
</div>
