<script>
  import Router from 'svelte-spa-router';
  import Nav from './components/Nav.svelte';
  import Home from './pages/Home.svelte';
  import Training from './pages/Training.svelte';
  import Dictionary from './pages/Dictionary.svelte';
  import Book from './pages/Book.svelte';
  import Login from './pages/Login.svelte';
  import { onMount } from 'svelte';
  import { onDestroy } from 'svelte';
  import { onAuthStateChanged } from "firebase/auth";
  import { auth } from "./lib/firebase.js";
  import { user, loading } from "./lib/auth.js";

  const routes = {
    '/': Home,
    '/training': Training,
    '/dictionary': Dictionary,
    '/book': Book,
    '/login': Login,
  };

  let isDesktop = false;

  function checkScreen() {
    isDesktop = window.innerWidth >= 1024;
  }

  onMount(() => {
    checkScreen();
    window.addEventListener('resize', checkScreen);

    onAuthStateChanged(auth, (u) => {
      if (u) {
        user.set({
          uid: u.uid,
          email: u.email,
          displayName: u.displayName,
          photoURL: u.photoURL,
        });
      } else {
        user.set(null);
      }
      loading.set(false);
    });
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
  {#if $loading}
    <div class="flex items-center justify-center min-h-[60vh]">
      <span class="text-2xl">Loading...</span>
    </div>
  {:else}
    <Router {routes} />
  {/if}
</main>