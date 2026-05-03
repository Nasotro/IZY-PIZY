<script>
  import { location } from 'svelte-spa-router';
  import { onMount } from 'svelte';
  import { onDestroy } from 'svelte';
  import { createEventDispatcher } from 'svelte';
  import { signOut } from "firebase/auth";
  import { auth } from "../lib/firebase.js";
  import { user } from "../lib/auth.js";

  export let isDesktop = false;

  const links = [
    { to: '/',           label: 'Home',       icon: '🏠' },
    { to: '/training',   label: 'Training',   icon: '🧠' },
    { to: '/dictionary', label: 'Dictionary', icon: '📖' },
    { to: '/book',       label: 'Book',       icon: '📚' },
  ];

  let darkMode = false;

  function isActive(current, to) {
    return to === '/' ? current === '/' : current.startsWith(to);
  }

  function toggleTheme() {
    darkMode = !darkMode;
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    localStorage.setItem('izipizy_theme', darkMode ? 'dark' : 'light');
  }

  async function logout() {
    await signOut(auth);
    user.set(null);
  }

  function checkScreen() {
    isDesktop = window.innerWidth >= 1024;
  }

  onMount(() => {
    const saved = localStorage.getItem('izipizy_theme');
    darkMode = saved === 'dark';
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    checkScreen();
    window.addEventListener('resize', checkScreen);
  });

  onDestroy(() => {
    if (typeof window !== 'undefined') {
      window.removeEventListener('resize', checkScreen);
    }
  });
</script>

{#if isDesktop}
<!-- Desktop: fixed top bar -->
<nav style="display: flex; align-items: center; justify-content: space-between; position: fixed; top: 0; left: 0; right: 0; z-index: 50; background-color: var(--color-bg-secondary); border-bottom: 2px solid var(--color-muted); height: 5rem; padding: 0 1.5rem; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
  
  <a href="#/" class="font-bold text-xl" style="color: var(--color-accent);">IZY PIZY 🥧</a>
  
  <div class="flex items-center gap-2" style="position: absolute; left: 50%; transform: translateX(-50%);">
    {#each links as { to, label, icon }}
      <a
        href="#{to}"
        class="flex items-center gap-3 text-lg font-medium px-6 py-3 rounded-lg transition-colors"
        style="color: {isActive($location, to) ? 'var(--color-accent)' : 'var(--color-secondary)'}; background-color: {isActive($location, to) ? 'rgba(199, 91, 57, 0.1)' : 'transparent'};"
      >
        <span class="text-base">{icon}</span>
        <span>{label}</span>
      </a>
    {/each}
  </div>
  
  <div class="flex items-center gap-3">
    {#if $user}
      <img src={$user.photoURL} alt="Profile" class="w-8 h-8 rounded-full" />
      <button
        on:click={logout}
        class="text-sm font-medium px-3 py-2 rounded-lg hover:bg-gray-100"
        style="color: var(--color-secondary);"
      >
        Déconnexion
      </button>
    {:else}
      <a
        href="#/login"
        class="text-sm font-medium px-4 py-2 rounded-lg"
        style="background-color: var(--color-accent); color: white;"
      >
        Connexion
      </a>
    {/if}
    <button
      on:click={toggleTheme}
      class="flex items-center justify-center w-10 h-10 rounded-lg transition-colors"
      style="color: var(--color-secondary);"
      title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      <span class="text-xl">{darkMode ? '☀️' : '🌙'}</span>
    </button>
  </div>
</nav>
{:else}
<!-- Mobile: fixed bottom bar -->
<nav style="position: fixed; bottom: 0; left: 0; right: 0; z-index: 50; display: flex; background-color: var(--color-bg-secondary); border-top: 2px solid var(--color-muted); height: 5rem; padding: 0.5rem;">
  {#each links as { to, label, icon }}
    <a
      href="#{to}"
      class="flex flex-col items-center justify-center flex-1"
      style="color: {isActive($location, to) ? 'var(--color-accent)' : 'var(--color-muted)'}"
    >
      <span class="text-4xl leading-none">{icon}</span>
      <span class="text-sm mt-1">{label}</span>
    </a>
  {/each}
  {#if $user}
    <button
      on:click={logout}
      class="flex flex-col items-center justify-center flex-1"
      style="color: var(--color-muted)"
    >
      <span class="text-2xl leading-none">🚪</span>
      <span class="text-xs mt-1">Logout</span>
    </button>
  {:else}
    <a
      href="#/login"
      class="flex flex-col items-center justify-center flex-1"
      style="color: var(--color-muted)"
    >
      <span class="text-2xl leading-none">🔐</span>
      <span class="text-xs mt-1">Login</span>
    </a>
  {/if}
</nav>
{/if}