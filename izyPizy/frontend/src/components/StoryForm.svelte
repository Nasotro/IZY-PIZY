<script>
  import { getPi, createStory, updateStory } from '../lib/api.js';

  /** @type {{ id: number, position: number, sentence?: string, word_0: string, word_1: string, word_2: string, word_3: string, word_4: string } | null} */
  export let story = null;

  /** @type {(saved: object) => void} */
  export let onSave = () => {};

  /** @type {() => void} */
  export let onCancel = () => {};

  const isEdit = story !== null;

  let position = story?.position ?? 0;
  let word_0 = story?.word_0 ?? '';
  let word_1 = story?.word_1 ?? '';
  let word_2 = story?.word_2 ?? '';
  let word_3 = story?.word_3 ?? '';
  let word_4 = story?.word_4 ?? '';
  let sentence = story?.sentence ?? '';

  let previewDigits = '';
  let previewLoading = false;
  let saving = false;
  let error = '';

  async function fetchPreview(pos) {
    if (pos < 0 || pos > 99) { previewDigits = ''; return; }
    previewLoading = true;
    try {
      const data = await getPi(pos * 10, 10);
      previewDigits = data.digits;
    } catch {
      previewDigits = '';
    } finally {
      previewLoading = false;
    }
  }

  // Reactive: fetch preview whenever position changes
  $: fetchPreview(position);

  $: pairs = previewDigits
    ? [0, 1, 2, 3, 4].map((i) => previewDigits.slice(i * 2, i * 2 + 2))
    : ['??', '??', '??', '??', '??'];

  async function handleSubmit() {
    error = '';
    if (!word_0 || !word_1 || !word_2 || !word_3 || !word_4) {
      error = 'All 5 words are required.';
      return;
    }
    saving = true;
    try {
      const payload = {
        position,
        word_0, word_1, word_2, word_3, word_4,
        sentence: sentence || null,
      };
      const saved = isEdit
        ? await updateStory(story.id, payload)
        : await createStory(payload);
      onSave(saved);
    } catch (e) {
      error = e.message;
    } finally {
      saving = false;
    }
  }
</script>

<div class="rounded-2xl border border-indigo-200 bg-indigo-50/40 p-5 shadow-sm">
  <h2 class="text-lg font-bold text-gray-800 mb-4">
    {isEdit ? 'Edit Story' : 'Add Story'}
  </h2>

  <form on:submit|preventDefault={handleSubmit} class="space-y-4">
    <!-- Position -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1" for="position">
        Position (0 = digits 1–10)
      </label>
      <input
        id="position"
        type="number"
        min="0"
        max="99"
        bind:value={position}
        class="w-full min-h-[44px] rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />
    </div>

    <!-- Pi digit preview -->
    <div class="rounded-lg bg-white border border-gray-200 px-4 py-3">
      <p class="text-xs text-gray-500 mb-2">
        Pi digits for position {position}&nbsp;
        (digits {position * 10 + 1}–{position * 10 + 10}):
      </p>
      {#if previewLoading}
        <p class="text-xs text-gray-400 italic">Loading…</p>
      {:else}
        <div class="grid grid-cols-5 gap-1 text-center">
          {#each pairs as pair, i}
            <span class="font-mono text-sm font-bold text-indigo-700 bg-indigo-50 rounded px-1 py-0.5">
              {pair}
            </span>
          {/each}
        </div>
      {/if}
    </div>

    <!-- 5 word inputs -->
    <div class="grid grid-cols-5 gap-2">
      <div class="flex flex-col items-center gap-1">
        <span class="font-mono text-xs text-gray-400">{pairs[0]}</span>
        <input type="text" bind:value={word_0} placeholder="Word 1"
          class="w-full min-h-[44px] rounded-lg border border-gray-300 px-2 py-2 text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div class="flex flex-col items-center gap-1">
        <span class="font-mono text-xs text-gray-400">{pairs[1]}</span>
        <input type="text" bind:value={word_1} placeholder="Word 2"
          class="w-full min-h-[44px] rounded-lg border border-gray-300 px-2 py-2 text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div class="flex flex-col items-center gap-1">
        <span class="font-mono text-xs text-gray-400">{pairs[2]}</span>
        <input type="text" bind:value={word_2} placeholder="Word 3"
          class="w-full min-h-[44px] rounded-lg border border-gray-300 px-2 py-2 text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div class="flex flex-col items-center gap-1">
        <span class="font-mono text-xs text-gray-400">{pairs[3]}</span>
        <input type="text" bind:value={word_3} placeholder="Word 4"
          class="w-full min-h-[44px] rounded-lg border border-gray-300 px-2 py-2 text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
      <div class="flex flex-col items-center gap-1">
        <span class="font-mono text-xs text-gray-400">{pairs[4]}</span>
        <input type="text" bind:value={word_4} placeholder="Word 5"
          class="w-full min-h-[44px] rounded-lg border border-gray-300 px-2 py-2 text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-400" />
      </div>
    </div>

    <!-- Sentence -->
    <div>
      <label class="block text-sm font-medium text-gray-700 mb-1" for="sentence">
        Sentence (optional)
      </label>
      <textarea
        id="sentence"
        bind:value={sentence}
        rows="2"
        placeholder="A short story linking the 5 words…"
        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
      ></textarea>
    </div>

    {#if error}
      <p class="text-sm text-red-600">{error}</p>
    {/if}

    <!-- Buttons -->
    <div class="flex gap-3 justify-end pt-1">
      <button
        type="button"
        on:click={onCancel}
        class="min-h-[44px] px-5 text-sm font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
      >
        Cancel
      </button>
      <button
        type="submit"
        disabled={saving}
        class="min-h-[44px] px-5 text-sm font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
      >
        {saving ? 'Saving…' : isEdit ? 'Save changes' : 'Add story'}
      </button>
    </div>
  </form>
</div>
