<script>
  export let size = 'md';
  export let message = '';

  const sizes = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4'
  };
</script>

<div class="flex flex-col items-center justify-center gap-3 py-8">
  <div class="{sizes[size]} border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
  {#if message}
    <p class="text-gray-500 text-sm md:text-base">{message}</p>
  {/if}
</div>