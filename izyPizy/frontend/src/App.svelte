<script>
  import Router from 'svelte-spa-router';
  import Nav from './components/Nav.svelte';
  import Home from './pages/Home.svelte';
  import Training from './pages/Training.svelte';
  import Dictionary from './pages/Dictionary.svelte';
  import Book from './pages/Book.svelte';
  import { onMount } from 'svelte';
  import { onDestroy } from 'svelte';

  const routes = {
    '/': Home,
    '/training': Training,
    '/dictionary': Dictionary,
    '/book': Book,
  };

  let isDesktop = false;

  function checkScreen() {
    isDesktop = window.innerWidth >= 1024;
  }

  onMount(() => {
    checkScreen();
    window.addEventListener('resize', checkScreen);
  });

  onDestroy(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('resize', checkScreen);
    }
  });
</script>

<Nav {isDesktop} />

<!-- Offset content so it isn't hidden behind nav bars -->
<main class="min-h-screen w-full" style="background-color: var(--color-dominant); padding-bottom: 5rem; padding-top: {isDesktop ? '5rem' : '0'}">
  <Router {routes} />
</main>
