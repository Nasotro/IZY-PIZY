<script>
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import { getStories, deleteStory, getPi } from '../lib/api.js';
  import StoryCard from '../components/StoryCard.svelte';
  import StoryForm from '../components/StoryForm.svelte';
  import ImageGenerationModal from '../components/ImageGenerationModal.svelte';
  import Loader from '../components/Loader.svelte';

  let stories = [];
  let piCache = new Map();
  let loading = true;
  let error = '';

  let formMode = null;
  let editingStory = null;
  let nextPosition = 0;
  let sortOrder = 'asc';

  // Currently selected 10-digit group (story id)
  let selectedId = null;

  // Track image generation state per story
  let generatingImageFor = {}; // { storyId: boolean }

  // Image generation modal state
  let showImageGenerationModal = false;
  let selectedStoryForGeneration = null;

  async function loadStories() {
    loading = true;
    error = '';
    try {
      stories = await getStories();
      nextPosition = stories.length > 0 ? Math.max(...stories.map(s => s.position)) + 1 : 0;
      await prefetchPi(stories);
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function prefetchPi(list) {
    const positions = [...new Set(list.map((s) => s.position))];
    await Promise.all(
      positions.map(async (pos) => {
        if (!piCache.has(pos)) {
          const data = await getPi(pos * 10, 10);
          piCache.set(pos, data.digits);
        }
      })
    );
    piCache = piCache;
  }

  function pairsFor(story) {
    const digits = piCache.get(story.position) ?? '';
    return digits
      ? [0, 1, 2, 3, 4].map((i) => digits.slice(i * 2, i * 2 + 2))
      : ['??', '??', '??', '??', '??'];
  }

  $: sortedStories = [...stories].sort((a, b) =>
    sortOrder === 'asc' ? a.position - b.position : b.position - a.position
  );

  $: selectedStory = stories.find((s) => s.id === selectedId) ?? null;

  function selectStory(id) {
    selectedId = id;
  }

  function closeDrawer() {
    selectedId = null;
  }

  function openCreate() {
    editingStory = null;
    formMode = 'create';
  }

  function openEdit(story) {
    editingStory = story;
    formMode = 'edit';
  }

  function closeForm() {
    formMode = null;
    editingStory = null;
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') closeForm();
  }

  function handleBackdropClick(e) {
    if (e.target === e.currentTarget) closeForm();
  }

  async function handleSave(saved) {
    closeForm();
    await loadStories();
    // Keep the edited story open, or select the newly created one
    if (saved && saved.id) selectedId = saved.id;
  }

  async function handleDelete(story) {
    if (!confirm(`Delete story at position ${story.position}?`)) return;
    try {
      await deleteStory(story.id);
      if (selectedId === story.id) selectedId = null;
      await loadStories();
    } catch (e) {
      alert('Failed to delete: ' + e.message);
    }
  }

  // Open image generation modal
  function openImageGenerationModal(story) {
    selectedStoryForGeneration = story;
    showImageGenerationModal = true;
  }

  // Close image generation modal
  function closeImageGenerationModal() {
    showImageGenerationModal = false;
    selectedStoryForGeneration = null;
  }

  // Handle completion of image generation from modal
  async function handleImageGenerationComplete(updatedStory) {
    closeImageGenerationModal();
    // Update the story in the local list
    stories = stories.map(s => s.id === updatedStory.id ? updatedStory : s);
    // Clear the generating state
    generatingImageFor = { ...generatingImageFor, [updatedStory.id]: false };
  }

  function toggleSort() {
    sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
  }

  onMount(loadStories);
</script>

<div class="w-full mx-auto px-4 py-6 md:py-8 lg:py-10 space-y-6 md:space-y-8">
  <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 md:gap-4">
    <h1 class="text-2xl md:text-3xl font-display" style="color: var(--color-secondary);">📖 Story Book</h1>
    <div class="flex items-center gap-2">
      {#if stories.length > 1}
        <button
          on:click={toggleSort}
          class="min-h-[44px] md:min-h-[48px] px-3 md:px-4 text-sm md:text-base font-mono font-bold uppercase tracking-wider btn-retro btn-retro-secondary flex items-center gap-1"
          title={sortOrder === 'asc' ? 'Sort descending' : 'Sort ascending'}
        >
          <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
          <span class="hidden sm:inline">Position</span>
        </button>
      {/if}
      {#if formMode === null}
        <button
          on:click={openCreate}
          class="min-h-[44px] md:min-h-[48px] px-5 md:px-6 text-sm md:text-base btn-retro btn-retro-primary"
        >
          + Add Story
        </button>
      {/if}
    </div>
  </div>

  {#if formMode !== null}
    <div
      class="fixed inset-0 z-40 bg-black/40"
      on:click={handleBackdropClick}
      on:keydown={handleKeydown}
      role="dialog"
      aria-modal="true"
      aria-label={formMode === 'edit' ? 'Edit Story' : 'Add Story'}
      tabindex="-1"
    >
      <div
        class="fixed bottom-0 left-0 right-0 z-50 rounded-t-2xl p-5 pb-24 md:p-6 md:pb-6 border-retro-thick shadow-retro-xl max-h-[80vh] overflow-y-auto
               sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:w-96 md:w-[480px] lg:w-[560px] sm:-translate-x-1/2 sm:-translate-y-1/2 sm:rounded-2xl"
        style="background-color: var(--color-dominant);"
        role="document"
      >
        <div class="mb-4 md:mb-5 flex items-center justify-between">
          <span class="text-xl md:text-2xl font-display" style="color: var(--color-secondary);">{formMode === 'edit' ? 'Edit Story' : 'Add Story'}</span>
          <button
            class="rounded-full p-1 md:p-2 hover:bg-theme-muted/5"
            style="color: var(--color-muted);"
            on:click={closeForm}
            aria-label="Close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 md:h-7 md:w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <StoryForm story={editingStory} nextPosition={formMode === 'create' ? nextPosition : undefined} onSave={handleSave} onCancel={closeForm} />
      </div>
    </div>
  {/if}

  {#if loading}
    <Loader message="Loading stories..." />
  {:else if error}
    <p class="text-center text-red-500 py-12 md:py-16 text-base md:text-lg">{error}</p>
  {:else if sortedStories.length === 0}
    <div class="text-center py-16 md:py-20" style="color: var(--color-muted);">
      <p class="text-4xl md:text-5xl mb-3">📭</p>
      <p class="text-lg md:text-xl font-display" style="color: var(--color-secondary);">No stories yet.</p>
      <p class="text-sm md:text-base mt-1">Click <span class="font-bold text-theme-accent">+ Add Story</span> to create one.</p>
    </div>
  {:else}
    <div class="md:grid md:grid-cols-[minmax(0,2fr)_minmax(0,3fr)] md:gap-6 md:items-start">
      <!-- Left: vertical list of 10-digit groups (scrollable on desktop) -->
      <div class="space-y-2 pb-4 md:pb-0 md:max-h-[calc(100vh-15rem)] md:overflow-y-auto md:pr-1.5">
        {#each sortedStories as story (story.id)}
          <button
            type="button"
            on:click={() => selectStory(story.id)}
            aria-pressed={selectedId === story.id}
            class="w-full text-left rounded-lg border-2 px-4 py-3 transition-colors {selectedId === story.id ? 'bg-theme-surface-alt shadow-retro' : 'bg-theme-surface hover:bg-theme-surface-alt shadow-sm'}"
            style="border-color: {selectedId === story.id
              ? 'var(--color-accent)'
              : 'var(--color-border)'};"
          >
            <div class="flex items-center justify-between gap-3">
              <div class="flex flex-wrap gap-1.5">
                {#each pairsFor(story) as pair}
                  <span class="font-mono text-sm md:text-base font-bold px-1.5 py-0.5 rounded border-2 {selectedId === story.id ? 'text-theme-accent border-theme-accent bg-theme-surface-alt' : 'text-theme-accent border-theme-muted bg-theme-surface-alt'}">{pair}</span>
                {/each}
              </div>
              <span class="text-xs whitespace-nowrap {selectedId === story.id ? 'text-theme-accent' : ''}" style="color: {selectedId === story.id ? 'var(--color-accent)' : 'var(--color-muted)'};">{story.position * 10 + 1} – {story.position * 10 + 10}</span>
            </div>
            <div class="mt-1.5 flex items-center gap-2 min-w-0">
              <span
                class="shrink-0 w-2 h-2 rounded-full"
                style="background-color: {story.image_url ? 'var(--color-accent)' : 'var(--color-muted)'}; opacity: {story.image_url ? 1 : 0.35};"
                title={story.image_url ? 'Image available' : 'No image'}
              ></span>
              {#if story.sentence}
                <p class="truncate text-sm text-theme-muted">{story.sentence}</p>
              {:else}
                <p class="truncate text-sm italic text-theme-muted" style="opacity: 0.5;">No sentence</p>
              {/if}
            </div>
          </button>
        {/each}
      </div>

      <!-- Right: story + image detail (slides in on selection) -->
      <div class="hidden md:block md:min-w-0">
        {#if selectedStory}
          {#key selectedStory.id}
            <div in:fly={{ x: 40, duration: 220 }}>
              <StoryCard
                story={selectedStory}
                piDigits={piCache.get(selectedStory.position) ?? ''}
                onEdit={() => openEdit(selectedStory)}
                onDelete={() => handleDelete(selectedStory)}
                onGenerateImage={() => openImageGenerationModal(selectedStory)}
                onOpenImageGeneration={() => openImageGenerationModal(selectedStory)}
                hasImageGenerationModal={true}
                generatingImage={generatingImageFor[selectedStory.id] ?? false}
              />
            </div>
          {/key}
        {:else}
          <div class="rounded-lg border-2 shadow-retro p-10 text-center bg-theme-surface" style="border-color: var(--color-border); color: var(--color-muted);">
            <p class="text-lg md:text-xl font-medium">Select a group of digits</p>
            <p class="text-sm md:text-base mt-1">Click a 10-digit group on the left to see its story and image.</p>
          </div>
        {/if}
      </div>
    </div>

    <!-- Mobile: detail slides in from the side as a drawer -->
    {#if selectedStory}
      <div class="fixed inset-0 z-30 md:hidden" role="dialog" aria-modal="true" aria-label="Story details">
        <div class="absolute inset-0 bg-black/40" on:click={closeDrawer}></div>
        <div
          class="drawer-panel absolute inset-y-0 right-0 w-full max-w-md overflow-y-auto p-4 border-l-[3px] shadow-retro-xl"
          style="background-color: var(--color-dominant); border-color: var(--color-border);"
        >
          <div class="mb-3 flex items-center justify-between">
            <button
              on:click={closeDrawer}
              class="flex items-center gap-1.5 min-h-[40px] px-3 text-sm btn-retro btn-retro-secondary"
            >
              ← Back
            </button>
            <span class="text-sm font-semibold text-theme-muted">Digits {selectedStory.position * 10 + 1} – {selectedStory.position * 10 + 10}</span>
          </div>
          <StoryCard
            story={selectedStory}
            piDigits={piCache.get(selectedStory.position) ?? ''}
            onEdit={() => openEdit(selectedStory)}
            onDelete={() => handleDelete(selectedStory)}
            onGenerateImage={() => openImageGenerationModal(selectedStory)}
            onOpenImageGeneration={() => openImageGenerationModal(selectedStory)}
            hasImageGenerationModal={true}
            generatingImage={generatingImageFor[selectedStory.id] ?? false}
          />
        </div>
      </div>
    {/if}
  {/if}

  <!-- Image Generation Modal -->
  {#if showImageGenerationModal && selectedStoryForGeneration}
    <ImageGenerationModal
      story={selectedStoryForGeneration}
      onClose={closeImageGenerationModal}
      onComplete={handleImageGenerationComplete}
    />
  {/if}
</div>

<style>
  .drawer-panel {
    animation: drawer-in 0.25s ease-out;
  }

  @keyframes drawer-in {
    from {
      transform: translateX(100%);
    }
    to {
      transform: translateX(0);
    }
  }
</style>
