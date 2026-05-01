<script>
  import { onMount } from 'svelte';
  import { getStories, deleteStory, getPi } from '../lib/api.js';
  import StoryCard from '../components/StoryCard.svelte';
  import StoryForm from '../components/StoryForm.svelte';
  import Loader from '../components/Loader.svelte';

  let stories = [];
  let piCache = new Map();
  let loading = true;
  let error = '';

  let formMode = null;
  let editingStory = null;
  let nextPosition = 0;

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

  onMount(loadStories);
</script>

<div class="w-full mx-auto px-4 py-6 md:py-8 lg:py-10 space-y-6 md:space-y-8">
  <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 md:gap-4">
    <h1 class="text-2xl md:text-3xl font-bold text-theme">📖 Story Book</h1>
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

  {#if formMode !== null}
    <StoryForm story={editingStory} nextPosition={formMode === 'create' ? nextPosition : undefined} onSave={handleSave} onCancel={closeForm} />
  {/if}

  {#if loading}
    <Loader message="Loading stories..." />
  {:else if error}
    <p class="text-center text-red-500 py-12 md:py-16 text-base md:text-lg">{error}</p>
  {:else if stories.length === 0}
    <div class="text-center py-16 md:py-20" style="color: var(--color-muted);">
      <p class="text-4xl md:text-5xl mb-3">📭</p>
      <p class="text-lg md:text-xl font-medium">No stories yet.</p>
      <p class="text-sm md:text-base mt-1">Click <span class="font-semibold">+ Add Story</span> to create one.</p>
    </div>
  {:else}
    <div class="space-y-4 md:space-y-6">
      {#each stories as story (story.id)}
        <StoryCard
          {story}
          piDigits={piCache.get(story.position) ?? ''}
          onEdit={() => openEdit(story)}
          onDelete={() => handleDelete(story)}
        />
      {/each}
    </div>
  {/if}
</div>