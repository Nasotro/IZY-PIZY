<script>
  export let size = 'md';
  export let message = '';

  const sizes = {
    sm: 'w-5 h-5 border-2',
    md: 'w-8 h-8 border-4',
    lg: 'w-12 h-12 border-4'
  };
</script>

<div class="flex flex-col items-center justify-center gap-3 py-8">
  <div class="{sizes[size]} rounded-full animate-spin" style="border-style: solid; border-color: var(--color-border); border-top-color: var(--color-accent);"></div>
  {#if message}
    <p class="font-mono text-sm md:text-base" style="color: var(--color-muted);">{message}</p>
  {/if}
</div>
