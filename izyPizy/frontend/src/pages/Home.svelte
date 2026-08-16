<script>
  const features = [
    {
      to: '/training',
      icon: '🧠',
      title: 'Training',
      description: 'Memorize digits of Pi with interactive exercises',
    },
    {
      to: '/dictionary',
      icon: '📖',
      title: 'Dictionary',
      description: 'Explore the Pi digit dictionary with word associations',
    },
    {
      to: '/book',
      icon: '📚',
      title: 'Book',
      description: 'Read stories encoded in Pi digits',
    },
  ];
</script>

<div class="w-full mx-auto px-4 py-8 md:py-12 lg:py-16 flex flex-col items-center gap-8 md:gap-12">
  <div class="text-center space-y-4 max-w-2xl">
    <p class="font-mono text-xs md:text-sm tracking-[0.3em] uppercase" style="color: var(--color-muted);">
      Memorize π · one story at a time
    </p>
    <h1 class="font-display text-4xl md:text-5xl lg:text-6xl leading-tight" style="color: var(--color-secondary);">
      Welcome to IZY PIZY 🥧
    </h1>
    <p class="text-lg md:text-xl" style="color: var(--color-muted);">
      Master the digits of Pi through fun exercises, stories, and mnemonics
    </p>
  </div>

  <div class="w-full max-w-3xl grid gap-6 md:gap-7">
    {#each features as { to, icon, title, description }, i}
      <a
        href="#{to}"
        class="group flex items-center gap-4 md:gap-5 p-5 md:p-6 border-2 hover:-translate-x-0.5 hover:-translate-y-0.5 transition-transform duration-100"
        style="background-color: var(--color-surface); border-color: var(--color-border); box-shadow: 5px 5px 0 0 var(--color-border);"
      >
        <div
          class="flex-shrink-0 w-14 h-14 md:w-16 md:h-16 border-2 flex items-center justify-center text-3xl md:text-4xl"
          style="border-color: var(--color-border); box-shadow: 3px 3px 0 0 var(--color-border); background-color: {i === 0 ? '#F4A261' : i === 1 ? 'var(--color-accent)' : '#2A9D8F'};"
        >
          {icon}
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-baseline gap-3">
            <span class="font-mono text-sm font-bold" style="color: var(--color-accent);">{String(i + 1).padStart(2, '0')}</span>
            <h2 class="font-display text-xl md:text-2xl" style="color: var(--color-secondary);">{title}</h2>
          </div>
          <p class="text-sm md:text-base mt-1" style="color: var(--color-muted);">{description}</p>
        </div>
        <div class="flex-shrink-0 text-2xl md:text-3xl transition-transform duration-100 group-hover:translate-x-1" style="color: var(--color-accent);">→</div>
      </a>
    {/each}
  </div>

  <div class="mt-4 text-center font-mono text-sm md:text-base" style="color: var(--color-muted);">
    <p>Pick a section above to get started</p>
  </div>
</div>
