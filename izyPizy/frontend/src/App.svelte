<script>
  import Nav from './components/Nav.svelte';
  import Home from './pages/Home.svelte';
  import Training from './pages/Training.svelte';
  import Dictionary from './pages/Dictionary.svelte';
  import Book from './pages/Book.svelte';
  import Login from './pages/Login.svelte';
  import Unauthorized from './pages/Unauthorized.svelte';
  import { onMount } from 'svelte';
  import { onAuthStateChanged } from "firebase/auth";
  import { auth } from "./lib/firebase.js";
  import { user, loading } from "./lib/auth.js";

  let currentRoute = '/';
  let isDesktop = false;
  let savedTarget = '';
  let authChecked = false;
  let navKey = 0;

  const routes = {
    '/': Home,
    '/login': Login,
    '/unauthorized': Unauthorized,
  };

  function getRoute() {
    let hash = window.location.hash.slice(1) || '/';
    if (hash === '' || hash === '/') return '/';
    
    if (hash === '/training' || hash === '/dictionary' || hash === '/book') {
      if (!$user) {
        savedTarget = hash;
        return '/unauthorized';
      }
      return hash;
    }
    
    if (hash === '/login') {
      if ($user) return '/';
      return hash;
    }
    
    if (routes[hash]) return hash;
    
    return '/';
  }

  function handleResize() {
    isDesktop = window.innerWidth >= 1024;
  }

  function handleHashChange() {
    currentRoute = getRoute();
    navKey++;
  }

  onMount(() => {
    isDesktop = window.innerWidth >= 1024;
    currentRoute = getRoute();
    
    window.addEventListener('resize', handleResize);
    window.addEventListener('hashchange', handleHashChange);

    const unsubscribe = onAuthStateChanged(auth, (u) => {
      if (u) {
        user.set({
          uid: u.uid,
          email: u.email,
          displayName: u.displayName,
          photoURL: u.photoURL,
        });
        if (savedTarget) {
          const target = savedTarget;
          savedTarget = '';
          currentRoute = target;
          window.location.hash = '#' + target;
        } else {
          currentRoute = getRoute();
        }
      } else {
        user.set(null);
        savedTarget = '';
        currentRoute = getRoute();
      }
      loading.set(false);
      authChecked = true;
      navKey++;
    });

    return unsubscribe;
  });
</script>

<Nav {isDesktop} />

<main class="min-h-screen w-full" style="background-color: var(--color-dominant); padding-bottom: 5rem; padding-top: {isDesktop ? '5rem' : '0'}">
  {#if currentRoute === '/training'}
    <Training />
  {:else if currentRoute === '/dictionary'}
    <Dictionary />
  {:else if currentRoute === '/book'}
    <Book />
  {:else if currentRoute === '/login'}
    <Login />
  {:else if currentRoute === '/unauthorized'}
    <Unauthorized />
  {:else}
    <Home />
  {/if}
</main>