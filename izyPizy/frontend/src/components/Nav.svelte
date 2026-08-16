<script>
  import { onMount } from 'svelte';
  import { signOut } from "firebase/auth";
  import { auth } from "../lib/firebase.js";
  import { user, isLocalUser, logoutLocal } from "../lib/auth.js";

  export let isDesktop = false;

  let darkMode = false;
  let currentRoute = window?.location?.hash?.slice(1) || '/';
  let tick = 0;

  const links = [
    { to: '/',           label: 'Home',       icon: '🏠' },
    { to: '/training',   label: 'Training',   icon: '🧠' },
    { to: '/dictionary', label: 'Dictionary', icon: '📖' },
    { to: '/book',       label: 'Book',       icon: '📚' },
  ];

  function isActive(to) {
    return to === '/' ? currentRoute === '/' : currentRoute.startsWith(to);
  }

  function toggleTheme() {
    darkMode = !darkMode;
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    localStorage.setItem('izipizy_theme', darkMode ? 'dark' : 'light');
  }

  async function logout() {
    if (isLocalUser($user)) {
      logoutLocal();
    } else {
      await signOut(auth);
      user.set(null);
    }
    window.location.hash = '#/';
  }

  onMount(() => {
    const saved = localStorage.getItem('izipizy_theme');
    darkMode = saved === 'dark';
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
    
    function updateRoute() {
      currentRoute = window.location.hash.slice(1) || '/';
      tick++;
    }
    
    window.addEventListener('hashchange', updateRoute);
    
    return () => {
      window.removeEventListener('hashchange', updateRoute);
    };
  });
</script>

{#key tick}
{#if isDesktop}
<nav style="display: flex; align-items: center; justify-content: space-between; position: fixed; top: 0; left: 0; right: 0; z-index: 50; background-color: var(--color-bg-secondary); border-bottom: 3px solid var(--color-border); height: 5rem; padding: 0 1.5rem;">
  
  <a href="#/" class="flex items-center gap-2 font-display text-xl" style="color: var(--color-secondary);">
    <span class="w-8 h-8 rounded-full flex items-center justify-center font-mono text-lg" style="background-color: var(--color-accent); color: var(--color-bg-tertiary); border: 2px solid var(--color-border); box-shadow: 2px 2px 0 0 var(--color-border);">π</span>
    IZY PIZY 🥧
  </a>
  
  <div class="flex items-center gap-1" style="position: absolute; left: 50%; transform: translateX(-50%);">
    {#each links as { to, label, icon }}
      <a
        href="#{to}"
        class="flex items-center gap-3 text-lg font-medium px-6 py-3 rounded-lg transition-colors"
        style="color: {isActive(to) ? 'var(--color-accent)' : 'var(--color-secondary)'}; box-shadow: {isActive(to) ? 'inset 0 -3px 0 var(--color-accent)' : 'none'}; opacity: {isActive(to) ? 1 : 0.75};"
      >
        <span class="text-base">{icon}</span>
        <span>{label}</span>
      </a>
    {/each}
  </div>
  
  <div class="flex items-center gap-3">
    {#if $user}
      {#if $user.photoURL}
        <img src={$user.photoURL} alt="Profile" class="w-8 h-8 rounded-full border-2" style="border-color: var(--color-border);" />
      {:else}
        <span class="w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2" style="background-color: var(--color-accent); color: var(--color-bg-tertiary); border-color: var(--color-border); box-shadow: 2px 2px 0 0 var(--color-border);">
          {($user.displayName || 'U').charAt(0).toUpperCase()}
        </span>
      {/if}
      <button
        onclick={logout}
        class="text-sm font-medium px-3 py-2 rounded-lg border-2 hover:bg-theme-surface-alt transition-colors"
        style="color: var(--color-secondary); border-color: var(--color-border);"
      >
        Déconnexion
      </button>
    {:else}
      <a
        href="#/login"
        class="text-sm font-medium px-4 py-2 rounded-lg shadow-retro-sm"
        style="background-color: var(--color-accent); color: var(--color-bg-tertiary); border: 2px solid var(--color-border);"
      >
        Connexion
      </a>
    {/if}
    <button
      onclick={toggleTheme}
      class="flex items-center justify-center w-10 h-10 rounded-lg border-2 hover:bg-theme-surface-alt transition-colors"
      style="color: var(--color-secondary); border-color: var(--color-border);"
      title={darkMode ? 'Switch to light mode' : 'Switch to dark mode'}
    >
      <span class="text-xl">{darkMode ? '☀️' : '🌙'}</span>
    </button>
  </div>
</nav>
{:else}
<nav style="position: fixed; bottom: 0; left: 0; right: 0; z-index: 50; display: flex; background-color: var(--color-bg-secondary); border-top: 3px solid var(--color-border); height: 5rem; padding: 0.5rem;">
  {#each links as { to, label, icon }}
    <a
      href="#{to}"
      class="flex flex-col items-center justify-center flex-1"
      style="color: {isActive(to) ? 'var(--color-accent)' : 'var(--color-muted)'}"
    >
      <span class="text-4xl leading-none">{icon}</span>
      <span class="text-sm mt-1 font-medium">{label}</span>
    </a>
  {/each}
  {#if $user}
    <button
      onclick={logout}
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
{/key}