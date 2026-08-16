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

  let allDigits = '';
  let displayDigits = '';

  let jumpOpen = false;
  let jumpValue = '';

  let flashTimer;

  let settingsOpen = false;
  let settings = {
    jumpEnabled: true,
    timerMode: false,
    errorMode: false
  };

  let timerRunning = false;
  let startTime = 0;
  let elapsedTime = 0;
  let timerInterval;
  let sessionStartTime = null;

  let errorStopped = false;

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

  $: cursorLineIndex = Math.floor(currentPosition / 10);
  $: cursorInLinePos = currentPosition % 10;

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
  <h1 class="text-2xl md:text-3xl font-display self-start" style="color: var(--color-secondary);">🧠 Training</h1>

  <div class="w-full text-center">
    <span class="font-mono text-xs md:text-sm tracking-[0.25em] uppercase" style="color: var(--color-muted);">Position</span>
    <p class="text-5xl md:text-6xl lg:text-7xl font-display leading-none mt-1" style="color: var(--color-accent); text-shadow: 3px 3px 0 var(--color-bg-secondary);">
      {currentPosition}
    </p>
    {#if settings.timerMode}
      <p class="text-2xl md:text-3xl font-mono font-bold mt-2" style="color: var(--color-secondary);">
        {formatTime(elapsedTime)}
      </p>
    {/if}
  </div>

  <div bind:this={digitsContainer} class="w-full space-y-1 overflow-y-auto max-h-40 md:max-h-48 lg:max-h-56 rounded-lg px-3 py-2 md:px-4 md:py-3" style="background-color: #1A1A1A; border: 2px solid var(--color-border); box-shadow: 5px 5px 0 0 #F4A261;">
    {#if loadingContext}
      <div class="flex items-center justify-center py-4">
        <Loader size="sm" message="Loading digits..." />
      </div>
    {:else}
    {#each digitLines as pairs, lineIdx}
      <div class="flex gap-2 md:gap-3 justify-center font-mono text-lg md:text-xl lg:text-2xl leading-tight">
        {#each pairs as pair}
          <span class="tracking-widest" style="color: #FAF3E3; opacity: 0.8;">{pair}</span>
        {/each}
        {#if lineIdx === cursorLineIndex && pairs.length < 5}
          <span class="animate-pulse" style="color: var(--color-accent);">_</span>
        {/if}
      </div>
    {/each}
    {#if digitLines.length === 0 || (digitLines.length > 0 && digitLines[digitLines.length - 1].length === 5 && cursorLineIndex >= digitLines.length)}
      <div class="flex gap-2 md:gap-3 justify-center font-mono text-lg md:text-xl lg:text-2xl leading-tight">
        <span class="animate-pulse" style="color: var(--color-accent);">_</span>
      </div>
    {/if}
    {/if}
  </div>

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
      class="w-full h-full rounded-xl border-4 text-center text-6xl md:text-7xl lg:text-8xl font-mono font-bold outline-none transition-colors duration-150 shadow-retro"
      style="
        {errorStopped
          ? 'border-color: var(--color-muted); background-color: var(--color-surface-alt); color: var(--color-muted);'
          : lastResult === 'correct'
          ? 'border-color: var(--color-success); background-color: var(--color-surface); color: var(--color-success);'
          : lastResult === 'wrong'
          ? 'border-color: var(--color-danger); background-color: var(--color-surface); color: var(--color-danger); animation: shake 0.35s ease;'
          : 'border-color: var(--color-accent); background-color: var(--color-surface); color: var(--color-secondary);'}
      "
    />
  </div>

  <div class="h-8 md:h-10 text-center">
    {#if errorStopped}
      <p class="font-display text-xl md:text-2xl" style="color: var(--color-danger);">GAME OVER!</p>
    {:else if lastResult === 'correct'}
      <p class="w-full text-center text-lg md:text-xl font-mono font-bold uppercase tracking-widest animate-pulse" style="color: var(--color-success);">✓ Correct!</p>
    {:else if lastResult === 'wrong'}
      <p class="w-full text-center text-lg md:text-xl font-mono font-bold uppercase tracking-widest" style="color: var(--color-danger);">
        ✗ Wrong! Expected: <span class="font-mono">{expectedDigit}</span>
      </p>
    {/if}
  </div>

  {#if errorStopped}
    <div class="flex flex-col items-center gap-4 w-full">
      <p class="text-base md:text-lg">You reached position <span class="font-bold text-theme-accent">{currentPosition}</span></p>
      <button
        on:click={reset}
        class="min-h-[44px] md:min-h-[48px] px-8 md:px-10 text-base md:text-lg btn-retro btn-retro-primary"
      >
        🔄 Restart
      </button>
    </div>
  {:else}
    <div class="flex gap-3 w-full justify-center flex-wrap">
      <button
        on:click={reset}
        class="min-h-[44px] md:min-h-[48px] px-6 md:px-8 text-sm md:text-base btn-retro btn-retro-secondary"
      >
        Reset
      </button>
      {#if settings.jumpEnabled}
        <button
          on:click={openJump}
          class="min-h-[44px] md:min-h-[48px] px-6 md:px-8 text-sm md:text-base btn-retro btn-retro-mustard"
        >
          Jump to…
        </button>
      {/if}
      <button
        on:click={() => { settingsOpen = !settingsOpen; }}
        class="min-h-[44px] md:min-h-[48px] px-6 md:px-8 text-sm md:text-base btn-retro btn-retro-secondary"
      >
        ⚙️ Settings
      </button>
    </div>
  {/if}

  {#if jumpOpen}
    <div class="w-full rounded-lg border-2 p-5 md:p-6 shadow-retro space-y-3" style="border-color: var(--color-accent); background-color: var(--color-surface);">
      <label class="block text-sm md:text-base font-mono font-bold uppercase tracking-wider" style="color: var(--color-secondary);" for="jump-input">
        Jump to position (0–999)
      </label>
      <input
        id="jump-input"
        type="number"
        min="0"
        max="999"
        bind:value={jumpValue}
        on:keydown={(e) => { if (e.key === 'Enter') confirmJump(); if (e.key === 'Escape') cancelJump(); }}
        class="w-full min-h-[44px] md:min-h-[48px] input-retro px-3 font-mono text-sm md:text-base"
      />
      <div class="flex gap-3 justify-end">
        <button
          on:click={cancelJump}
          class="min-h-[44px] md:min-h-[48px] px-4 md:px-5 text-sm md:text-base btn-retro btn-retro-secondary"
        >
          Cancel
        </button>
        <button
          on:click={confirmJump}
          class="min-h-[44px] md:min-h-[48px] px-4 md:px-5 text-sm md:text-base btn-retro btn-retro-primary"
        >
          Go
        </button>
      </div>
    </div>
  {/if}

  {#if settingsOpen}
    <div
      class="fixed inset-0 flex items-center justify-center z-50 p-4"
      style="background-color: rgba(0,0,0,0.6);"
      on:click|self={() => settingsOpen = false}
      on:keydown={(e) => { if (e.key === 'Escape') settingsOpen = false; }}
      role="dialog"
      aria-modal="true"
      tabindex="-1"
    >
      <div class="w-full max-w-md rounded-lg border-retro-thick p-6 md:p-8 shadow-retro-xl space-y-6" style="background-color: var(--color-dominant);">
        <div class="flex items-center justify-between">
          <h2 class="text-xl md:text-2xl font-display" style="color: var(--color-secondary);">Training Settings</h2>
          <button
            on:click={() => settingsOpen = false}
            class="leading-none text-2xl hover:opacity-70"
            style="color: var(--color-muted);"
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
              class="w-5 h-5"
              style="accent-color: var(--color-accent);"
            />
            <span class="text-base text-theme">Enable "Jump to" button</span>
          </label>

          <label class="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              bind:checked={settings.timerMode}
              on:change={saveSettings}
              class="w-5 h-5"
              style="accent-color: var(--color-accent);"
            />
            <span class="text-base text-theme">Timer mode (show timer & store results)</span>
          </label>

          <label class="flex items-center gap-3 cursor-pointer">
            <input
              type="checkbox"
              bind:checked={settings.errorMode}
              on:change={saveSettings}
              class="w-5 h-5"
              style="accent-color: var(--color-accent);"
            />
            <span class="text-base text-theme">Error mode (reset on wrong answer)</span>
          </label>
        </div>

        <button
          on:click={() => settingsOpen = false}
          class="w-full min-h-[44px] md:min-h-[48px] text-base btn-retro btn-retro-primary"
        >
          Done
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-8px); }
    40% { transform: translateX(8px); }
    60% { transform: translateX(-6px); }
    80% { transform: translateX(6px); }
  }
</style>