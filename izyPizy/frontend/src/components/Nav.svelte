<script>
  import { location } from 'svelte-spa-router';

  const links = [
    { to: '/',           label: 'Training',   icon: '🧠' },
    { to: '/dictionary', label: 'Dictionary', icon: '📖' },
    { to: '/book',       label: 'Book',       icon: '📚' },
  ];

  function isActive(current, to) {
    return to === '/' ? current === '/' : current.startsWith(to);
  }
</script>

<!-- Mobile: fixed bottom bar -->
<nav class="fixed bottom-0 left-0 right-0 z-50 flex md:hidden bg-white border-t border-gray-200 shadow-lg">
  {#each links as { to, label, icon }}
    <a
      href="#{to}"
      class="flex flex-col items-center justify-center flex-1 py-2 text-xs gap-0.5
             {isActive($location, to) ? 'text-indigo-600 font-semibold' : 'text-gray-500 hover:text-indigo-500'}"
    >
      <span class="text-xl leading-none">{icon}</span>
      <span>{label}</span>
    </a>
  {/each}
</nav>

<!-- Desktop: fixed top bar -->
<nav class="hidden md:flex fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-200 shadow-sm px-6 h-14 items-center gap-8">
  <span class="font-bold text-indigo-600 text-lg mr-4">IZY PIZY 🥧</span>
  {#each links as { to, label, icon }}
    <a
      href="#{to}"
      class="flex items-center gap-1.5 text-sm font-medium px-2 py-1 rounded
             {isActive($location, to) ? 'text-indigo-600 bg-indigo-50' : 'text-gray-600 hover:text-indigo-500'}"
    >
      <span>{icon}</span>
      <span>{label}</span>
    </a>
  {/each}
</nav>
