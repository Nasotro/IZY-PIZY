<script>
  import Router from 'svelte-spa-router';
  import Nav from './components/Nav.svelte';
  import Training from './pages/Training.svelte';
  import Dictionary from './pages/Dictionary.svelte';
  import Book from './pages/Book.svelte';

  const routes = {
    '/': Training,
    '/dictionary': Dictionary,
    '/book': Book,
  };
</script>

<Nav />

<!-- Offset content so it isn't hidden behind nav bars -->
<main class="pb-20 md:pb-0 md:pt-14 min-h-screen bg-gray-50">
  <Router {routes} />
</main>
