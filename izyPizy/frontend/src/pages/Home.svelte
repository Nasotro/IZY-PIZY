<script>
  const features = [
    {
      to: '/training',
      icon: '🧠',
      title: 'Training',
      description: 'Memorize digits of Pi with interactive exercises',
      color: 'bg-[#C75B39]/5 border-[#C75B39]/20 hover:bg-[#C75B39]/10',
      iconBg: 'bg-[#C75B39]/10 text-[#C75B39]',
    },
    {
      to: '/dictionary',
      icon: '📖',
      title: 'Dictionary',
      description: 'Explore the Pi digit dictionary with word associations',
      color: 'bg-[#4A4036]/5 border-[#4A4036]/20 hover:bg-[#4A4036]/10',
      iconBg: 'bg-[#4A4036]/10 text-[#4A4036]',
    },
    {
      to: '/book',
      icon: '📚',
      title: 'Book',
      description: 'Read stories encoded in Pi digits',
      color: 'bg-[#4A4036]/5 border-[#4A4036]/20 hover:bg-[#4A4036]/10',
      iconBg: 'bg-[#4A4036]/10 text-[#4A4036]',
    },
  ];
</script>

<div class="w-full mx-auto px-4 py-8 md:py-12 lg:py-16 flex flex-col items-center gap-8 md:gap-12">
  <div class="text-center space-y-4 max-w-2xl">
    <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-[#4A4036]">
      Welcome to IZY PIZY 🥧
    </h1>
    <p class="text-lg md:text-xl text-[#4A4036]/70">
      Master the digits of Pi through fun exercises, stories, and mnemonics
    </p>
  </div>

  <div class="w-full max-w-3xl grid gap-5 md:gap-6">
    {#each features as { to, icon, title, description, color, iconBg }}
      <a
        href="#{to}"
        class="flex items-center gap-4 md:gap-5 p-5 md:p-6 rounded-2xl border-2 transition-all duration-200 {color}"
      >
        <div class="flex-shrink-0 w-14 h-14 md:w-16 md:h-16 rounded-2xl flex items-center justify-center text-3xl md:text-4xl {iconBg}">
          {icon}
        </div>
        <div class="flex-1 min-w-0">
          <h2 class="text-xl md:text-2xl font-bold text-[#4A4036]">{title}</h2>
          <p class="text-sm md:text-base text-[#4A4036]/70 mt-1">{description}</p>
        </div>
        <div class="flex-shrink-0 text-[#4A4036]/40 text-2xl md:text-3xl">→</div>
      </a>
    {/each}
  </div>

  <div class="mt-4 text-center text-[#4A4036]/50 text-sm md:text-base">
    <p>Pick a section above to get started</p>
  </div>
</div>