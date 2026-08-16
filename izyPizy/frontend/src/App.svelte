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
  import { user, loading, getStoredLocalUser } from "./lib/auth.js";
  import { detectLocalMode } from "./lib/localMode.js";

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

    let unsubscribe = null;

    detectLocalMode().then((localMode) => {
      if (localMode) {
        // Local mode: restore the persisted local user, no Firebase involved.
        const localUser = getStoredLocalUser();
        if (localUser) {
          user.set(localUser);
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
        return;
      }

      unsubscribe = onAuthStateChanged(auth, (u) => {
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
    });

    return () => {
      if (unsubscribe) unsubscribe();
    };
  });
</script>

<Nav {isDesktop} />

<div class="retro-bg" aria-hidden="true">
  <div class="retro-bg__circles"></div>
  <div class="retro-bg__circles retro-bg__circles--bottom"></div>
  <span class="retro-bg__pi">π</span>
  <span class="retro-bg__digits retro-bg__digits--bottom">3.1415926535 8979323846 2643383279 5028841971 6939937510 5820974944 5923078164 0628620899 8628034825 3421170679</span>
  <span class="retro-bg__digits retro-bg__digits--side">3.1415926535 8979323846 2643383279 5028841971 6939937510 5820974944 5923078164 0628620899 8628034825 3421170679</span>
</div>

<main class="relative z-10 min-h-screen w-full" style="padding-bottom: 5rem; padding-top: {isDesktop ? '5rem' : '0'}">
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