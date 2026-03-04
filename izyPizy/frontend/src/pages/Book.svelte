<script>
  import { onMount } from 'svelte';
  import { getStories, deleteStory, getPi } from '../lib/api.js';
  import StoryCard from '../components/StoryCard.svelte';
  import StoryForm from '../components/StoryForm.svelte';

  /** @type {Array<object>} */
  let stories = [];

  /** @type {Map<number, string>} position → 10-digit string */
  let piCache = new Map();

  let loading = true;
  let error = '';

  // Form state: null = hidden, 'create' = new, object = edit
  let formMode = null;
  /** @type {object|null} */
  let editingStory = null;

  async function loadStories() {
    loading = true;
    error = '';
    try {
      stories = await getStories();
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
    piCache = piCache; // trigger reactivity
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

<div class="max-w-2xl mx-auto px-4 py-6 space-y-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <h1 class="text-2xl font-bold text-gray-800">📖 Story Book</h1>
    {#if formMode === null}
      <button
        on:click={openCreate}
        class="min-h-[44px] px-5 text-sm font-semibold text-white bg-indigo-600 rounded-xl hover:bg-indigo-700 transition-colors shadow-sm"
      >
        + Add Story
      </button>
    {/if}
  </div>

  <!-- Form (create or edit) -->
  {#if formMode !== null}
    <StoryForm
      story={editingStory}
      onSave={handleSave}
      onCancel={closeForm}
    />
  {/if}

  <!-- Loading / error -->
  {#if loading}
    <p class="text-center text-gray-400 py-12">Loading stories…</p>
  {:else if error}
    <p class="text-center text-red-500 py-12">{error}</p>
  {:else if stories.length === 0}
    <div class="text-center py-16 text-gray-400">
      <p class="text-4xl mb-3">📭</p>
      <p class="text-lg font-medium">No stories yet.</p>
      <p class="text-sm mt-1">Click <span class="font-semibold">+ Add Story</span> to create one.</p>
    </div>
  {:else}
    <div class="space-y-4">
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
