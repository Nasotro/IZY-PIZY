<script>
  import { onMount } from 'svelte';
  import { getStories, deleteStory, getPi, generateStoryImage, generateStoryImageBatch } from '../lib/api.js';
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
  }

  async function handleDelete(story) {
    if (!confirm(`Delete story at position ${story.position}?`)) return;
    try {
      await deleteStory(story.id);
      await loadStories();
    } catch (e) {
      alert('Failed to delete: ' + e.message);
    }
  }

  // Handle image generation
  async function handleGenerateImage(story) {
    if (!story.sentence) {
      alert('Story has no sentence to generate an image from.');
      return;
    }
    
    generatingImageFor = { ...generatingImageFor, [story.id]: true };
    try {
      const updatedStory = await generateStoryImage(story.id);
      // Update the story in the local list
      stories = stories.map(s => s.id === story.id ? updatedStory : s);
    } catch (e) {
      alert('Failed to generate image: ' + e.message);
    } finally {
      generatingImageFor = { ...generatingImageFor, [story.id]: false };
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

  $: sortedStories = [...stories].sort((a, b) => 
    sortOrder === 'asc' ? a.position - b.position : b.position - a.position
  );

  onMount(loadStories);
</script>

<div class="w-full mx-auto px-4 py-6 md:py-8 lg:py-10 space-y-6 md:space-y-8">
  <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 md:gap-4">
    <h1 class="text-2xl md:text-3xl font-bold text-theme">📖 Story Book</h1>
    <div class="flex items-center gap-2">
      {#if stories.length > 1}
        <button
          on:click={toggleSort}
          class="min-h-[44px] md:min-h-[48px] px-3 md:px-4 text-sm md:text-base font-medium border rounded-lg hover:bg-theme-accent/5 transition-colors flex items-center gap-1"
          style="color: var(--color-accent); border-color: var(--color-accent);"
          title={sortOrder === 'asc' ? 'Sort descending' : 'Sort ascending'}
        >
          <span>{sortOrder === 'asc' ? '↑' : '↓'}</span>
          <span class="hidden sm:inline">Position</span>
        </button>
      {/if}
      {#if formMode === null}
        <button
          on:click={openCreate}
          class="min-h-[44px] md:min-h-[48px] px-5 md:px-6 text-sm md:text-base font-semibold rounded-xl transition-colors shadow-sm"
          style="color: var(--color-dominant); background-color: var(--color-accent);"
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
        class="fixed bottom-0 left-0 right-0 z-50 rounded-t-2xl p-5 pb-24 md:p-6 md:pb-6 shadow-2xl max-h-[80vh] overflow-y-auto
               sm:bottom-auto sm:left-1/2 sm:top-1/2 sm:w-96 md:w-[480px] lg:w-[560px] sm:-translate-x-1/2 sm:-translate-y-1/2 sm:rounded-2xl"
        style="background-color: var(--color-dominant);"
        role="document"
      >
        <div class="mb-4 md:mb-5 flex items-center justify-between">
          <span class="text-xl md:text-2xl font-bold text-theme">{formMode === 'edit' ? 'Edit Story' : 'Add Story'}</span>
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
      <p class="text-lg md:text-xl font-medium">No stories yet.</p>
      <p class="text-sm md:text-base mt-1">Click <span class="font-semibold">+ Add Story</span> to create one.</p>
    </div>
  {:else}
    <div class="space-y-4 md:space-y-6">
      {#each sortedStories as story (story.id)}
        <StoryCard
          {story}
          piDigits={piCache.get(story.position) ?? ''}
          onEdit={() => openEdit(story)}
          onDelete={() => handleDelete(story)}
          onGenerateImage={() => handleGenerateImage(story)}
          onOpenImageGeneration={() => openImageGenerationModal(story)}
          hasImageGenerationModal={true}
          generatingImage={generatingImageFor[story.id] ?? false}
        />
      {/each}
    </div>
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
