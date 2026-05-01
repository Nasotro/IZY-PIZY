<script>
  import { getPi, createStory, updateStory } from '../lib/api.js';
  import Loader from './Loader.svelte';

  /** @type {{ id: number, position: number, sentence?: string, word_0: string, word_1: string, word_2: string, word_3: string, word_4: string } | null} */
  export let story = null;

  /** @type {number | undefined} */
  export let nextPosition = undefined;

  /** @type {(saved: object) => void} */
  export let onSave = () => {};

  /** @type {() => void} */
  export let onCancel = () => {};

  const isEdit = story !== null;

  let position = story
    ? story.position
    : typeof nextPosition === 'number'
      ? nextPosition
      : 0;
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

<div class="rounded-2xl border border-[#C75B39]/20 bg-[#F5F2EE] p-5 shadow-sm">
  <h2 class="text-lg font-bold text-[#4A4036] mb-4">
    {isEdit ? 'Edit Story' : 'Add Story'}
  </h2>

  <form on:submit|preventDefault={handleSubmit} class="space-y-4">
    <!-- Pi digit preview -->
    <div class="rounded-lg bg-white border border-[#4A4036]/10 px-4 py-3 md:px-5 md:py-4">
      <p class="text-xs md:text-sm text-[#4A4036]/60 mb-2">
        Pi digits for position {position}&nbsp;
        (digits {position * 10 + 1}–{position * 10 + 10}):
      </p>
      {#if previewLoading}
        <Loader size="sm" />
      {:else}
        <div class="grid grid-cols-5 gap-1 md:gap-2 text-center">
          {#each pairs as pair, i}
            <span class="font-mono text-sm md:text-base font-bold text-[#C75B39] bg-[#C75B39]/5 rounded px-1 py-0.5">
              {pair}
            </span>
          {/each}
        </div>
      {/if}
    </div>

    <!-- 5 word inputs -->
    <div class="grid grid-cols-5 gap-2 md:gap-3">
      <div class="flex flex-col items-center gap-1">
        <span class="font-mono text-xs md:text-sm text-[#4A4036]/40">{pairs[0]}</span>
        <input type="text" bind:value={word_0} placeholder="Word 1"
          class="w-full min-h-[44px] md:min-h-[48px] rounded-lg border border-[#4A4036]/30 px-2 py-2 text-sm md:text-base text-center focus:outline-none focus:ring-2 focus:ring-[#C75B39]/40" />
      </div>
      <div class="flex flex-col items-center gap-1">
        <span class="font-mono text-xs md:text-sm text-[#4A4036]/40">{pairs[1]}</span>
        <input type="text" bind:value={word_1} placeholder="Word 2"
          class="w-full min-h-[44px] md:min-h-[48px] rounded-lg border border-[#4A4036]/30 px-2 py-2 text-sm md:text-base text-center focus:outline-none focus:ring-2 focus:ring-[#C75B39]/40" />
      </div>
      <div class="flex flex-col items-center gap-1">
        <span class="font-mono text-xs md:text-sm text-[#4A4036]/40">{pairs[2]}</span>
        <input type="text" bind:value={word_2} placeholder="Word 3"
          class="w-full min-h-[44px] md:min-h-[48px] rounded-lg border border-[#4A4036]/30 px-2 py-2 text-sm md:text-base text-center focus:outline-none focus:ring-2 focus:ring-[#C75B39]/40" />
      </div>
      <div class="flex flex-col items-center gap-1">
        <span class="font-mono text-xs md:text-sm text-[#4A4036]/40">{pairs[3]}</span>
        <input type="text" bind:value={word_3} placeholder="Word 4"
          class="w-full min-h-[44px] md:min-h-[48px] rounded-lg border border-[#4A4036]/30 px-2 py-2 text-sm md:text-base text-center focus:outline-none focus:ring-2 focus:ring-[#C75B39]/40" />
      </div>
      <div class="flex flex-col items-center gap-1">
        <span class="font-mono text-xs md:text-sm text-[#4A4036]/40">{pairs[4]}</span>
        <input type="text" bind:value={word_4} placeholder="Word 5"
          class="w-full min-h-[44px] md:min-h-[48px] rounded-lg border border-[#4A4036]/30 px-2 py-2 text-sm md:text-base text-center focus:outline-none focus:ring-2 focus:ring-[#C75B39]/40" />
      </div>
    </div>

    <!-- Sentence -->
    <div>
      <label class="block text-sm md:text-base font-medium text-[#4A4036] mb-1 md:mb-2" for="sentence">
        Sentence (optional)
      </label>
      <textarea
        id="sentence"
        bind:value={sentence}
        rows="2"
        placeholder="A short story linking the 5 words…"
        class="w-full rounded-lg border border-[#4A4036]/30 px-3 py-2 text-sm md:text-base focus:outline-none focus:ring-2 focus:ring-[#C75B39]/40 resize-none"
      ></textarea>
    </div>

    {#if error}
      <p class="text-sm md:text-base text-red-500">{error}</p>
    {/if}

    <!-- Buttons -->
    <div class="flex gap-3 justify-end pt-1 md:pt-2">
      <button
        type="button"
        on:click={onCancel}
        class="min-h-[44px] md:min-h-[48px] px-5 md:px-6 text-sm md:text-base font-medium text-[#4A4036] border border-[#4A4036]/30 rounded-lg hover:bg-[#4A4036]/5 transition-colors"
      >
        Cancel
      </button>
      <button
        type="submit"
        disabled={saving}
        class="min-h-[44px] md:min-h-[48px] px-5 md:px-6 text-sm md:text-base font-semibold text-[#FEFCF9] bg-[#C75B39] rounded-lg hover:bg-[#A84829] disabled:opacity-50 transition-colors"
      >
        {saving ? 'Saving…' : isEdit ? 'Save changes' : 'Add story'}
      </button>
    </div>
  </form>
</div>
