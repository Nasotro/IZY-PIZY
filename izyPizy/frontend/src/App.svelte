<script>
  import { Router, Route } from 'svelte-routing';
  import Nav from './components/Nav.svelte';
  import Training from './pages/Training.svelte';
  import Dictionary from './pages/Dictionary.svelte';
  import Book from './pages/Book.svelte';

  export let url = '';
</script>

<Router {url}>
  <Nav />

  <!-- Offset content so it isn't hidden behind nav bars -->
  <main class="pb-20 md:pb-0 md:pt-14 min-h-screen bg-gray-50">
    <Route path="/" component={Training} />
    <Route path="/dictionary" component={Dictionary} />
    <Route path="/book" component={Book} />
  </main>
</Router>
