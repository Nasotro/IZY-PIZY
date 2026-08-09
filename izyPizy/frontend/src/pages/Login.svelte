<script>
  import { onMount } from 'svelte';
  import { signInWithPopup } from "firebase/auth";
  import { auth, googleProvider } from "../lib/firebase.js";
  import { user } from "../lib/auth.js";
  import { loginLocal } from "../lib/auth.js";
  import { detectLocalMode } from "../lib/localMode.js";

  let error = "";
  let localMode = false;

  onMount(() => {
    detectLocalMode().then((m) => (localMode = m));
  });

  async function loginWithGoogle() {
    error = "";
    try {
      const result = await signInWithPopup(auth, googleProvider);
      user.set({
        uid: result.user.uid,
        email: result.user.email,
        displayName: result.user.displayName,
        photoURL: result.user.photoURL,
      });
    } catch (e) {
      error = e.message;
    }
  }

  function loginLocally() {
    loginLocal();
    window.location.hash = '#/';
  }
</script>

<div class="flex flex-col items-center justify-center min-h-[60vh] px-4">
  <h1 class="text-3xl font-bold mb-8" style="color: var(--color-accent)">
    IZY PIZY
  </h1>
  
  <div class="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
    <p class="text-gray-600 mb-8">Connectez-vous pour accéder à votre progression</p>
    
    <button
      on:click={loginWithGoogle}
      class="w-full flex items-center justify-center gap-3 bg-white border-2 border-gray-200 rounded-lg px-6 py-3 hover:bg-gray-50 transition-colors"
    >
      <svg class="w-5 h-5" viewBox="0 0 24 24">
        <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
        <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.96 20.53 7.7 23 12 23z"/>
        <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
        <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.96 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
      </svg>
      <span class="font-medium text-gray-700">Se connecter avec Google</span>
    </button>

    {#if localMode}
      <div class="flex items-center gap-3 my-6">
        <div class="flex-1 h-px bg-gray-200"></div>
        <span class="text-xs text-gray-400">ou</span>
        <div class="flex-1 h-px bg-gray-200"></div>
      </div>

      <button
        on:click={loginLocally}
        class="w-full flex items-center justify-center gap-3 bg-gray-100 border-2 border-gray-200 rounded-lg px-6 py-3 hover:bg-gray-200 transition-colors"
      >
        <span class="text-lg">💻</span>
        <span class="font-medium text-gray-700">Continuer sans compte (mode local)</span>
      </button>
      <p class="mt-3 text-xs text-gray-400">
        Aucune connexion Internet requise — vos données restent sur cet ordinateur.
      </p>
    {/if}
    
    {#if error}
      <p class="mt-4 text-red-500 text-sm">{error}</p>
    {/if}
  </div>
</div>