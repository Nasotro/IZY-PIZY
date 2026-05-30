<script>
  // Pi digits - first 10 digits after 3. (3.1415926535...)
  // We'll display: 3 . 14 15 92 65 35
  const piDigits = ['3', '14', '15', '92', '65', '35'];

  // Calculate dynamic font size based on viewport
  let fontSize = 4;
  let containerWidth = 0;
  let containerHeight = 0;

  function calculateFontSize() {
    if (containerWidth === 0 || containerHeight === 0) return;
    
    // Calculate available space per group
    const groupsCount = piDigits.length;
    const availableWidthPerGroup = containerWidth / groupsCount;
    const availableHeight = containerHeight;
    
    // Use the smaller dimension to ensure it fits
    const maxFontSize = Math.min(
      availableWidthPerGroup * 0.8,
      availableHeight * 0.6
    );
    
    fontSize = Math.max(12, Math.min(120, maxFontSize));
  }

  function handleResize() {
    const container = document.getElementById('pi-container');
    if (container) {
      containerWidth = container.clientWidth;
      containerHeight = container.clientHeight;
      calculateFontSize();
    }
  }

  import { onMount } from 'svelte';
  
  onMount(() => {
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  });
</script>

<div class="w-full min-h-screen flex flex-col items-center justify-center p-4 md:p-8">
  <div class="text-center mb-8 md:mb-12">
    <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold text-theme mb-4">
      Pi Visualizer 🥧
    </h1>
    <p class="text-lg md:text-xl text-theme-muted/70">
      First 10 digits of π separated into 5 groups of 2
    </p>
  </div>

  <div 
    id="pi-container"
    class="w-full max-w-4xl mx-auto flex items-center justify-center flex-wrap gap-2 md:gap-4 lg:gap-6"
    bind:clientWidth={containerWidth}
    bind:clientHeight={containerHeight}
  >
    <!-- Decimal point -->
    <span class="text-theme font-bold opacity-60" style="font-size: {fontSize}px">
      .
    </span>
    
    <!-- Pi digit groups -->
    {#each piDigits as digit, index}
      {#if index === 0}
        <!-- First digit (3) - larger and highlighted -->
        <span 
          class="text-theme-accent font-bold transition-all duration-300"
          style="font-size: {fontSize * 1.2}px"
        >
          {digit}
        </span>
      {:else}
        <!-- Other digit groups -->
        <span 
          class="text-theme font-bold transition-all duration-300 pi-digit-group"
          style="font-size: {fontSize}px"
        >
          {digit}
        </span>
      {/if}
    {/each}
  </div>

  <div class="mt-12 md:mt-16 text-center text-theme-muted/60">
    <p class="text-sm md:text-base">
      Resize your window to see the responsive behavior
    </p>
    <p class="text-xs md:text-sm mt-2 text-theme-muted/40">
      π ≈ 3.1415926535...
    </p>
  </div>
</div>

<style>
  .pi-digit-group {
    animation: pulse 2s infinite ease-in-out;
  }
  
  .pi-digit-group:nth-child(2) { animation-delay: 0.1s; }
  .pi-digit-group:nth-child(3) { animation-delay: 0.2s; }
  .pi-digit-group:nth-child(4) { animation-delay: 0.3s; }
  .pi-digit-group:nth-child(5) { animation-delay: 0.4s; }
  .pi-digit-group:nth-child(6) { animation-delay: 0.5s; }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
  }
  
  /* Responsive adjustments */
  @media (max-width: 640px) {
    .pi-digit-group {
      animation: none;
    }
  }
</style>
