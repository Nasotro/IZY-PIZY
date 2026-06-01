<script>
  // Full pi digits string (first 1000 digits after 3.)
  const fullPiDigits = '1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679821480865132823066470938446095505822317253594081284811174502841027019385211055596446229489549303819644288109756659334461284756482337867831652712019091456485669234603486104543266482133936072602491412737245870066063155881748815209209628292540917153643678925903600113305305488204665213841469519415116094330572703657595919530921861173819326117931051185480744623799627495673518857527248912279381830119491298336733624406566430860213949463952247371907021798609437027705392171762931767523846748184676694051320005681271452635608277857713427577896091736371787214684409012249534301465495853710507922796892589235420199561121290219608640344181598136297747713099605187072113499999983729780499510597317328160963185950244594553469083026425223082533446850352619311881710100031378387528865875332083814206171776691473035982534904287554687311595628638823537875937519577818577805321712268066130019278766111959092164201989';
  
  // Configuration options
  let digitCount = 50; // Number of digits to display (excluding the 3)
  let groupSize = 2; // How many digits per group
  let showAnimation = true; // Whether to show the pulse animation
  let colorScheme = 'accent'; // Color scheme: 'accent', 'rainbow', 'monochrome'
  
  // Calculate the pi digits based on configuration
  $: piDigits = calculatePiDigits();
  
  function calculatePiDigits() {
    const digits = fullPiDigits.substring(0, digitCount);
    const groups = [];
    
    // Always start with '3' as the first element
    groups.push('3');
    
    // Split remaining digits into groups
    for (let i = 0; i < digits.length; i += groupSize) {
      const group = digits.substring(i, i + groupSize);
      groups.push(group);
    }
    
    return groups;
  }

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

  // Rainbow colors for digit groups
  const rainbowColors = [
    '#ef4444', // red
    '#f97316', // orange
    '#eab308', // yellow
    '#22c55e', // green
    '#3b82f6', // blue
    '#6366f1', // indigo
    '#a855f7', // purple
  ];

  function getDigitColor(index) {
    if (colorScheme === 'rainbow') {
      if (index === 0) return rainbowColors[0]; // First digit (3) is red
      return rainbowColors[(index - 1) % rainbowColors.length];
    }
    return null; // Use CSS classes for other schemes
  }

  import { onMount } from 'svelte';
  
  onMount(() => {
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  });
</script>

<div class="w-full min-h-screen flex flex-col items-center p-4 md:p-8">
  <div class="text-center mb-6 md:mb-8">
    <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold text-theme mb-2">
      Pi Visualizer 🥧
    </h1>
    <p class="text-lg md:text-xl text-theme-muted/70">
      Visualize and customize Pi digits display
    </p>
  </div>

  <!-- Configuration Panel -->
  <div class="w-full max-w-4xl mx-auto mb-8 p-4 md:p-6 rounded-2xl bg-theme-surface-alt border border-theme-muted/20">
    <h2 class="text-xl md:text-2xl font-bold text-theme mb-5">
      Configuration Options
    </h2>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
      <!-- Digit Count Slider -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-theme">
          Number of Digits: {digitCount}
        </label>
        <input
          type="range"
          min="2"
          max="1000"
          step="2"
          bind:value={digitCount}
          class="w-full h-2 rounded-lg appearance-none cursor-pointer bg-theme-muted/20"
        />
        <div class="flex justify-between text-xs text-theme-muted/60">
          <span>2</span>
          <span>1000</span>
        </div>
      </div>

      <!-- Group Size Selector -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-theme">
          Group Size: {groupSize}
        </label>
        <select
          bind:value={groupSize}
          class="w-full p-2 rounded-lg bg-theme-surface border border-theme-muted/30 text-theme"
        >
          <option value="1">1 digit</option>
          <option value="2">2 digits</option>
          <option value="3">3 digits</option>
          <option value="4">4 digits</option>
          <option value="5">5 digits</option>
        </select>
      </div>

      <!-- Color Scheme Selector -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-theme">
          Color Scheme
        </label>
        <select
          bind:value={colorScheme}
          class="w-full p-2 rounded-lg bg-theme-surface border border-theme-muted/30 text-theme"
        >
          <option value="accent">Accent Theme</option>
          <option value="rainbow">Rainbow</option>
          <option value="monochrome">Monochrome</option>
        </select>
      </div>

      <!-- Animation Toggle -->
      <div class="space-y-2">
        <label class="block text-sm font-medium text-theme">
          Animation
        </label>
        <label class="flex items-center cursor-pointer">
          <input
            type="checkbox"
            bind:checked={showAnimation}
            class="sr-only"
          />
          <div class="relative w-12 h-6 rounded-full bg-theme-muted/20">
            <div 
              class="absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-theme-accent transition-transform duration-300"
              style="transform: {showAnimation ? 'translateX(100%)' : 'translateX(0)'}"
            ></div>
          </div>
          <span class="ml-3 text-sm text-theme">
            {showAnimation ? 'On' : 'Off'}
          </span>
        </label>
      </div>
    </div>
  </div>

  <!-- Pi Visualization -->
  <div 
    id="pi-container"
    class="w-full max-w-4xl mx-auto flex items-center justify-center flex-wrap gap-2 md:gap-4 lg:gap-6 p-4 md:p-6 rounded-2xl bg-theme-surface border border-theme-muted/20"
    bind:clientWidth={containerWidth}
    bind:clientHeight={containerHeight}
  >
    <!-- Decimal point -->
    <span 
      class="font-bold opacity-60 transition-all duration-300"
      class:text-theme-accent={colorScheme === 'accent'}
      class:text-theme={colorScheme === 'monochrome'}
      style="font-size: {fontSize}px; color: {colorScheme === 'rainbow' ? '#a855f7' : ''}"
    >
      .
    </span>
    
    <!-- Pi digit groups -->
    {#each piDigits as digit, index}
      {#if index === 0}
        <!-- First digit (3) - larger and highlighted -->
        <span 
          class="font-bold transition-all duration-300"
          class:text-theme-accent={colorScheme === 'accent'}
          class:text-theme={colorScheme === 'monochrome'}
          style="font-size: {fontSize * 1.2}px; color: {colorScheme === 'rainbow' ? getDigitColor(index) : ''}"
        >
          {digit}
        </span>
      {:else}
        <!-- Other digit groups -->
        <span 
          class="font-bold transition-all duration-300"
          class:pi-digit-group={showAnimation}
          class:text-theme={colorScheme === 'accent' || colorScheme === 'monochrome'}
          style="font-size: {fontSize}px; color: {colorScheme === 'rainbow' ? getDigitColor(index) : ''}"
        >
          {digit}
        </span>
      {/if}
    {/each}
  </div>

  <!-- Info and Stats -->
  <div class="mt-8 md:mt-12 text-center text-theme-muted/60">
    <p class="text-sm md:text-base">
      Showing {digitCount} digits of π in groups of {groupSize}
    </p>
    <p class="text-xs md:text-sm mt-2 text-theme-muted/40">
      π ≈ 3.{fullPiDigits.substring(0, 50)}...
    </p>
    <p class="text-xs md:text-sm mt-1 text-theme-muted/40">
      Resize your window to see the responsive behavior
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
  .pi-digit-group:nth-child(7) { animation-delay: 0.6s; }
  .pi-digit-group:nth-child(8) { animation-delay: 0.7s; }
  .pi-digit-group:nth-child(9) { animation-delay: 0.8s; }
  .pi-digit-group:nth-child(10) { animation-delay: 0.9s; }
  .pi-digit-group:nth-child(11) { animation-delay: 1.0s; }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.05); }
  }
  
  /* Range slider styling for WebKit browsers */
  input[type="range"]::-webkit-slider-thumb {
    appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--color-accent);
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  input[type="range"]::-webkit-slider-thumb:hover {
    transform: scale(1.2);
    box-shadow: 0 0 10px rgba(199, 91, 57, 0.5);
  }
  
  input[type="range"]::-moz-range-thumb {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--color-accent);
    cursor: pointer;
    border: none;
  }
  
  /* Responsive adjustments */
  @media (max-width: 640px) {
    .pi-digit-group {
      animation: none;
    }
  }
</style>
