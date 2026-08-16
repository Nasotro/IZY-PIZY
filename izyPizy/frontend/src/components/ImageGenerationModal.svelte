<script>
  import { generateStoryImageBatch, getImageUrl, setStoryImage, getEnhancedPromptPreview } from '../lib/api.js';
  import Loader from './Loader.svelte';

  /** @type {{ id: number, position: number, sentence: string, word_0: string, word_1: string, word_2: string, word_3: string, word_4: string, image_path: string | null }} */
  export let story = null;
  
  /** @type {() => void} */
  export let onClose = () => {};
  
  /** @type {(updatedStory: object) => void} */
  export let onComplete = () => {};

  // Configuration options
  let numImages = 3;
  let customPrompt = '';
  let useMistralEnhancement = false;
  let autoRephrase = true;
  let selectedModel = 'flux-2-pro';
  let baseWidth = 1024;
  let baseHeight = 1024;
  let sizeFactor = 'M'; // S, M, L, XL
  
  // Size multipliers
  const sizeOptions = [
    { id: 'S', label: 'S (Small)', multiplier: 0.5 },
    { id: 'M', label: 'M (Medium)', multiplier: 1 },
    { id: 'L', label: 'L (Large)', multiplier: 1.5 },
    { id: 'XL', label: 'XL (Extra Large)', multiplier: 2 }
  ];
  
  // Helper to get current size option
  function getSizeOption(id) {
    return sizeOptions.find(opt => opt.id === id) || sizeOptions[1];
  }
  
  // Reactive: compute width and height based on base dimensions and size factor
  $: width = Math.round(baseWidth * getSizeOption(sizeFactor).multiplier);
  $: height = Math.round(baseHeight * getSizeOption(sizeFactor).multiplier);
  
  // Available models for Blackforest (synced with backend WORKING_MODELS)
  const availableModels = [
    { id: 'flux-2-pro', name: 'FLUX.2 Pro', description: 'Stable FLUX.2 Pro - Best balance' },
    { id: 'flux-2-pro-preview', name: 'FLUX.2 Pro (Preview)', description: 'Latest FLUX.2 Pro' },
    { id: 'flux-2-max', name: 'FLUX.2 Max', description: 'Maximum quality' },
    { id: 'flux-2-flex', name: 'FLUX.2 Flex', description: 'Flexible model' },
    { id: 'flux-2-klein-9b', name: 'FLUX.2 Klein 9B', description: 'Fast 9B model' },
    { id: 'flux-2-klein-4b', name: 'FLUX.2 Klein 4B', description: 'Fast 4B model' },
    { id: 'flux-pro-1.1', name: 'FLUX 1.1 Pro', description: 'FLUX 1.1 Pro' },
    { id: 'flux-pro-1.1-ultra', name: 'FLUX 1.1 Ultra', description: 'FLUX 1.1 Ultra' },
    { id: 'flux-pro', name: 'FLUX Pro', description: 'Original FLUX Pro' },
    { id: 'flux', name: 'FLUX', description: 'Base FLUX model' }
  ];

  // Available aspect ratios
  const aspectRatios = [
    { w: 1024, h: 1024, label: '1:1 (Square)' },
    { w: 1152, h: 896, label: '16:13 (Landscape)' },
    { w: 896, h: 1152, label: '13:16 (Portrait)' },
    { w: 1360, h: 768, label: '16:9 (Widescreen)' },
    { w: 768, h: 1360, label: '9:16 (Mobile)' }
  ];

  // State
  let generating = false;
  let generatedImages = []; // { url: string, path: string, selected: boolean }[]
  let generationProgress = []; // Track progress for each image
  let error = '';
  let previewPrompt = '';
  let enhancedPrompt = '';
  let fetchingEnhancedPrompt = false;
  let showAdvancedSettings = false;

  // Initialize custom prompt from story sentence
  $: customPrompt = customPrompt || (story && story.sentence) || '';

  // Build the key elements from the story's 5 words
  $: keyElements = story ? [story.word_0, story.word_1, story.word_2, story.word_3, story.word_4].filter(w => w && w.trim()).join(', ') : '';

  // Preview the prompt that will be used
  $: previewPrompt = (customPrompt || (story && story.sentence) || '') + (useMistralEnhancement ? ' (enhanced with Mistral)' : '') + ' - ' + width + 'x' + height + ' - Model: ' + selectedModel + (keyElements ? ' - Key elements: ' + keyElements : '');

  // Fetch enhanced prompt preview
  async function fetchEnhancedPrompt() {
    if (!customPrompt && !story?.sentence) return;
    
    fetchingEnhancedPrompt = true;
    error = '';
    
    try {
      const prompt = customPrompt || story.sentence;
      const keyElements = story ? [story.word_0, story.word_1, story.word_2, story.word_3, story.word_4].filter(w => w && w.trim()) : [];
      const response = await withTimeout(getEnhancedPromptPreview(prompt, keyElements.length > 0 ? keyElements : null));
      enhancedPrompt = response.enhanced_prompt || response.original_prompt || 'Enhanced version of: ' + JSON.stringify(prompt);
    } catch (e) {
      error = e.message || 'Failed to fetch enhanced prompt preview';
      enhancedPrompt = customPrompt || story?.sentence || '';
    } finally {
      fetchingEnhancedPrompt = false;
    }
  }

  async function handleGenerate() {
    if (!story) return;
    
    generating = true;
    error = '';
    generatedImages = [];
    generationProgress = Array(numImages).fill({ status: 'pending', progress: 0 });

    try {
      const response = await withTimeout(generateStoryImageBatch(story.id, {
        num_images: numImages,
        custom_prompt: customPrompt || null,
        use_mistral_enhancement: useMistralEnhancement,
        model: selectedModel,
        width: width,
        height: height,
        auto_rephrase: autoRephrase
      }));

      // Handle the response
      if (response && response.images) {
        generatedImages = response.images.map((img, index) => ({
          url: getImageUrl(img.path),
          path: img.path,
          selected: index === 0 // Auto-select the first one
        }));
      } else if (response && response.image_path) {
        // Fallback: single image generated
        generatedImages = [{
          url: getImageUrl(response.image_path),
          path: response.image_path,
          selected: true
        }];
      }
    } catch (e) {
      error = e.message || 'Failed to generate images';
    } finally {
      generating = false;
    }
  }

  function selectImage(index) {
    generatedImages = generatedImages.map((img, i) => ({
      ...img,
      selected: i === index
    }));
  }

  async function handleApply() {
    const selectedImage = generatedImages.find(img => img.selected);
    if (selectedImage && story) {
      // Update the story with the selected image
      try {
        const updatedStory = await withTimeout(setStoryImage(story.id, selectedImage.path));
        onComplete(updatedStory);
      } catch (e) {
        error = 'Failed to set selected image: ' + (e.message || String(e));
      }
    }
  }

  function handleCancel() {
    if (generating) {
      if (confirm('Are you sure you want to cancel image generation?')) {
        // In a real implementation, we'd need to cancel the backend request
        generating = false;
        onClose();
      }
    } else {
      onClose();
    }
  }

  function setAspectRatio(ratio) {
    baseWidth = ratio.w;
    baseHeight = ratio.h;
  }

  // Helper function to get aspect ratio button class
  function getAspectRatioClass(ratio) {
    const isActive = width === ratio.w && height === ratio.h;
    return 'px-3 py-2 rounded-lg text-sm transition-all border-2 ' + 
      (isActive ? 'border-accent bg-accent/10 shadow-retro-sm' : 'border-ink/40 hover:border-ink');
  }

  // Helper function to get image button class
  function getImageButtonClass(image) {
    return 'relative group rounded-lg overflow-hidden border-4 transition-all ' + 
      (image.selected ? 'border-accent shadow-retro' : 'border-transparent hover:border-muted/40');
  }

  // Handle keydown for ESC
  function handleKeydown(e) {
    if (e.key === 'Escape' && !generating) {
      onClose();
    }
  }

  // Handle backdrop click
  function handleBackdropClick(e) {
    if (e.target === e.currentTarget && !generating) {
      onClose();
    }
  }

  // Toggle advanced settings
  function toggleAdvancedSettings() {
    showAdvancedSettings = !showAdvancedSettings;
  }

  // Timeout helper function (60 seconds)
  function withTimeout(promise, ms = 60000) {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Request timed out after ${ms/1000} seconds`));
      }, ms);
      promise
        .then((result) => {
          clearTimeout(timeoutId);
          resolve(result);
        })
        .catch((error) => {
          clearTimeout(timeoutId);
          reject(error);
        });
    });
  }
</script>

<div
  class="fixed inset-0 z-50 flex items-center justify-center p-4"
  on:click={handleBackdropClick}
  on:keydown={handleKeydown}
  role="dialog"
  aria-modal="true"
  aria-label="Image Generation Options"
  tabindex="-1"
>
  <!-- Backdrop -->
  <div class="fixed inset-0 bg-black/60 backdrop-blur-sm"></div>

  <!-- Modal -->
  <div
    class="relative w-full max-w-4xl max-h-[90vh] bg-theme-surface rounded-lg border-retro-thick shadow-retro-xl overflow-hidden overflow-y-auto"
    role="document"
  >
    <!-- Header -->
    <div class="sticky top-0 z-10 bg-theme-surface border-b-2 px-6 py-4 flex items-center justify-between" style="border-color: var(--color-border);">
      <h2 class="text-xl font-display" style="color: var(--color-secondary);">Generate Image</h2>
      <button
        on:click={handleCancel}
        class="rounded-full p-2 hover:bg-theme-muted/5 transition-colors"
        style="color: var(--color-muted);"
        aria-label="Close"
        disabled={generating}
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Content -->
    <div class="p-6 space-y-6">
      
      <!-- Story Preview -->
      {#if story}
        <div class="rounded-lg bg-theme-surface-alt border-2 p-4" style="border-color: var(--color-border);">
          <p class="text-sm text-theme-muted mb-1">Story:</p>
          <p class="text-lg font-medium text-theme">{story.sentence || 'No sentence'}</p>
          {#if keyElements}
            <p class="text-sm text-theme-muted mt-2">
              <span class="font-medium">Key elements:</span> {keyElements}
            </p>
          {/if}
        </div>
      {/if}

      <!-- Customization Options -->
      <div class="space-y-5">
        
        <!-- Custom Prompt (Always visible) -->
        <div>
          <label class="block text-sm font-medium text-theme mb-2">
            Custom Prompt (optional)
            <span class="text-theme-muted/60 text-xs">- Leave empty to use story sentence</span>
          </label>
          <textarea
            bind:value={customPrompt}
            rows="3"
            placeholder="Enter a custom prompt for the image generation..."
            class="w-full input-retro px-3 py-2 text-sm resize-none"
            disabled={generating}
          ></textarea>
          <p class="text-xs text-theme-muted/60 mt-1">
            Tip: Be descriptive! Include colors, styles, and details for better results.
          </p>
        </div>

        <!-- Advanced Settings Dropdown -->
        <div class="border-t-2 pt-4" style="border-color: var(--color-border);">
          <button
            on:click={toggleAdvancedSettings}
            class="w-full flex items-center justify-between p-4 rounded-lg border-2 hover:bg-theme-surface-alt transition-colors"
            style="border-color: var(--color-border);"
            disabled={generating}
          >
            <span class="text-sm font-medium text-theme flex items-center gap-2">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd" />
              </svg>
              Advanced Settings
            </span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 transition-transform" style="transform: {showAdvancedSettings ? 'rotate(180deg)' : 'rotate(0deg)'};" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
          </button>

          {#if showAdvancedSettings}
            <div class="mt-4 space-y-5">
              <!-- Number of Images -->
              <div class="flex items-center justify-between">
                <div>
                  <label class="block text-sm font-medium text-theme mb-1">Number of Images</label>
                  <p class="text-xs text-theme-muted/60">Generate multiple variations to choose from</p>
                </div>
                <div class="flex items-center gap-3">
                  <button
                    on:click={() => numImages = Math.max(1, numImages - 1)}
                    disabled={generating || numImages <= 1}
                    class="w-8 h-8 rounded-lg border-2 flex items-center justify-center hover:bg-theme-surface-alt disabled:opacity-50"
                    style="color: var(--color-secondary); border-color: var(--color-border);"
                  >
                    - 
                  </button>
                  <span class="text-lg font-bold min-w-[30px] text-center" style="color: var(--color-accent);">{numImages}</span>
                  <button
                    on:click={() => numImages = Math.min(10, numImages + 1)}
                    disabled={generating || numImages >= 10}
                    class="w-8 h-8 rounded-lg border-2 flex items-center justify-center hover:bg-theme-surface-alt disabled:opacity-50"
                    style="color: var(--color-secondary); border-color: var(--color-border);"
                  >
                    + 
                  </button>
                </div>
              </div>

              <!-- Mistral Enhancement Toggle -->
              <div class="flex items-center justify-between">
                <div>
                  <label class="block text-sm font-medium text-theme mb-1">Mistral Prompt Enhancement</label>
                  <p class="text-xs text-theme-muted/60">Enrich your prompt with AI for better results</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    bind:checked={useMistralEnhancement}
                    class="sr-only peer"
                    disabled={generating}
                  >
                  <div class="w-11 h-6 rounded-full border-2 peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-muted/40 after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent" style="background-color: var(--color-surface-alt); border-color: var(--color-border);"></div>
                </label>
              </div>

              <!-- Auto Rephrase Toggle -->
              <div class="flex items-center justify-between">
                <div>
                  <label class="block text-sm font-medium text-theme mb-1">Auto Fix Copyright Issues</label>
                  <p class="text-xs text-theme-muted/60">Automatically rephrase prompts that trigger moderation errors</p>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    bind:checked={autoRephrase}
                    class="sr-only peer"
                    disabled={generating}
                  >
                  <div class="w-11 h-6 rounded-full border-2 peer peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-muted/40 after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent" style="background-color: var(--color-surface-alt); border-color: var(--color-border);"></div>
                </label>
              </div>

              {#if useMistralEnhancement}
                <div class="ml-auto">
                  <button
                    on:click={fetchEnhancedPrompt}
                    disabled={fetchingEnhancedPrompt || generating}
                    class="text-sm px-3 py-1.5 btn-retro btn-retro-secondary"
                  >
                    {fetchingEnhancedPrompt ? 'Previewing...' : 'Preview Enhanced Prompt'}
                  </button>
                </div>
                
                {#if enhancedPrompt}
                  <div class="rounded-lg bg-theme-surface-alt border-2 p-3" style="border-color: var(--color-accent);">
                    <p class="text-xs font-medium text-theme-accent mb-1">Enhanced Prompt Preview:</p>
                    <p class="text-sm text-theme">{enhancedPrompt}</p>
                  </div>
                {/if}
              {/if}

              <!-- Model Selection -->
              <div>
                <label class="block text-sm font-medium text-theme mb-2">Image Model</label>
                <select
                  bind:value={selectedModel}
                  class="w-full input-retro px-3 py-2 text-sm"
                  disabled={generating}
                >
                  {#each availableModels as model}
                    <option value={model.id}>{model.name} - {model.description}</option>
                  {/each}
                </select>
              </div>

              <!-- Size Factor -->
              <div>
                <label class="block text-sm font-medium text-theme mb-2">Image Size</label>
                <div class="grid grid-cols-4 gap-2">
                  {#each sizeOptions as size}
                    <button
                      on:click={() => sizeFactor = size.id}
                      class="px-3 py-2 rounded-lg text-sm font-medium transition-all border-2 {sizeFactor === size.id ? 'border-accent bg-accent/10 shadow-retro-sm' : 'border-ink/40 hover:border-ink'}"
                      style="color: {sizeFactor === size.id ? 'var(--color-accent)' : 'var(--color-secondary)'};"
                      disabled={generating}
                    >
                      {size.label}
                    </button>
                  {/each}
                </div>
                <p class="text-xs text-theme-muted/60 mt-1">
                  Current: {width} × {height} pixels
                </p>
              </div>

              <!-- Aspect Ratio -->
              <div>
                <label class="block text-sm font-medium text-theme mb-2">Image Dimensions</label>
                <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-2">
                  {#each aspectRatios as ratio}
                    <button
                      on:click={() => setAspectRatio(ratio)}
                      class={getAspectRatioClass(ratio)}
                      style="color: {baseWidth === ratio.w && baseHeight === ratio.h ? 'var(--color-accent)' : 'var(--color-secondary)'};"
                      disabled={generating}
                    >
                      {ratio.label}
                    </button>
                  {/each}
                </div>
                <div class="flex items-center gap-2 mt-2 text-sm">
                  <input
                    type="number"
                    bind:value={baseWidth}
                    class="w-20 input-retro px-2 py-1 text-sm"
                    disabled={generating}
                  >
                  <span class="text-theme-muted">x</span>
                  <input
                    type="number"
                    bind:value={baseHeight}
                    class="w-20 input-retro px-2 py-1 text-sm"
                    disabled={generating}
                  >
                  <span class="text-xs text-theme-muted/60">pixels</span>
                </div>
              </div>
            </div>
          {/if}
        </div>

      </div>

      <!-- Prompt Preview -->
      <div class="rounded-lg bg-theme-surface-alt border border-theme-muted/10 p-4">
        <p class="text-sm font-medium text-theme mb-2">Prompt Preview:</p>
        <p class="text-sm text-theme font-mono whitespace-pre-wrap">{previewPrompt}</p>
      </div>

      <!-- Generate Button -->
      <button
        on:click={handleGenerate}
        disabled={generating || (!story?.sentence && !customPrompt)}
        class="w-full min-h-[48px] text-lg btn-retro btn-retro-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {#if generating}
          <Loader size="sm" />
          Generating {generatedImages.length}/{numImages} images...
        {:else}
          Generate Images
        {/if}
      </button>

      {#if error}
        <p class="text-sm text-red-500 text-center">{error}</p>
      {/if}

      <!-- Generated Images Grid -->
      {#if generatedImages.length > 0}
        <div class="space-y-4">
          <h3 class="text-lg font-semibold text-theme">Select Your Image</h3>
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {#each generatedImages as image, index}
              <button
                on:click={() => selectImage(index)}
                class={getImageButtonClass(image)}
              >
                <img
                  src={image.url}
                  alt="Generated image {index + 1}"
                  class="w-full h-48 object-cover"
                >
                <div class="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  {#if image.selected}
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-white" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  {:else}
                    <span class="text-white text-sm font-medium">Select</span>
                  {/if}
                </div>
                <div class="absolute bottom-2 left-2 bg-black/70 text-white text-xs px-2 py-1 rounded">
                  Image {index + 1}
                </div>
              </button>
            {/each}
          </div>

          <div class="flex gap-3 justify-end pt-2">
            <button
              on:click={handleCancel}
              class="min-h-[44px] px-5 text-sm btn-retro btn-retro-secondary"
            >
              Cancel
            </button>
            <button
              on:click={handleApply}
              class="min-h-[44px] px-5 text-sm btn-retro btn-retro-primary"
            >
              Apply Selected Image
            </button>
          </div>
        </div>
      {/if}

      {#if generating && generatedImages.length === 0}
        <div class="text-center py-6">
          <Loader message="Generating your images..." />
          <p class="text-sm text-theme-muted mt-2">This may take a few minutes...</p>
        </div>
      {/if}
    </div>
  </div>
</div>
