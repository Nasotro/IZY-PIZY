<script>
  import { signInWithPopup, GoogleAuthProvider } from "firebase/auth";
  import { auth } from "../lib/firebase.js";

  let provider = new GoogleAuthProvider();
  let error = $state('');
  let loading = $state(false);

  async function handleLogin() {
    error = '';
    loading = true;
    try {
      await signInWithPopup(auth, provider);
    } catch (e) {
      error = e.message;
      loading = false;
    }
  }
</script>

<div class="unauthorized-container">
  <div class="bg-pattern"></div>
  <div class="content">
    <div class="lock-icon">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
      </svg>
    </div>
    
    <h1>Access Restricted</h1>
    <p class="message">You need to be connected to access this page</p>
    
    <button class="login-btn" onclick={handleLogin} disabled={loading}>
      {#if loading}
        <span>Connecting...</span>
      {:else}
        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
          <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        Sign in with Google
      {/if}
    </button>
    
    {#if error}
      <p class="error-message">{error}</p>
    {/if}
  </div>
</div>

<style>
  .unauthorized-container {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    text-align: center;
    padding: 2rem;
    overflow: hidden;
  }

  .bg-pattern {
    position: absolute;
    inset: 0;
    background: 
      radial-gradient(circle at 20% 80%, rgba(102, 126, 234, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 80% 20%, rgba(118, 75, 162, 0.15) 0%, transparent 50%),
      radial-gradient(circle at 50% 50%, rgba(102, 126, 234, 0.05) 0%, transparent 70%);
    animation: bgShift 10s ease-in-out infinite;
  }

  @keyframes bgShift {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.7;
    }
  }

  .content {
    position: relative;
    z-index: 1;
    animation: fadeIn 0.6s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .lock-icon {
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1.5rem;
    box-shadow: 
      0 10px 40px rgba(102, 126, 234, 0.3),
      0 0 0 0 rgba(102, 126, 234, 0.4);
    animation: pulse 3s infinite, float 4s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% {
      box-shadow: 
        0 10px 40px rgba(102, 126, 234, 0.3),
        0 0 0 0 rgba(102, 126, 234, 0.4);
    }
    50% {
      box-shadow: 
        0 10px 60px rgba(102, 126, 234, 0.4),
        0 0 0 15px rgba(102, 126, 234, 0);
    }
  }

  @keyframes float {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-10px);
    }
  }

  .lock-icon svg {
    width: 48px;
    height: 48px;
    color: white;
  }

  h1 {
    font-size: 2.5rem;
    font-weight: 800;
    color: #1a1a2e;
    margin: 0 0 0.75rem;
    letter-spacing: -0.02em;
  }

  .message {
    font-size: 1.25rem;
    color: #6b7280;
    margin: 0 0 2.5rem;
    max-width: 400px;
    line-height: 1.6;
  }

  .login-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1.125rem 2.5rem;
    font-size: 1.0625rem;
    font-weight: 600;
    color: white;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 9999px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 
      0 4px 15px rgba(102, 126, 234, 0.35),
      0 0 0 0 rgba(102, 126, 234, 0.5);
  }

  .login-btn:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 
      0 12px 35px rgba(102, 126, 234, 0.45),
      0 0 0 8px rgba(102, 126, 234, 0.1);
  }

  .login-btn:active {
    transform: translateY(-1px) scale(1);
  }

  .login-btn svg {
    width: 24px;
    height: 24px;
  }

  @media (max-width: 640px) {
    .lock-icon {
      width: 80px;
      height: 80px;
    }

    .lock-icon svg {
      width: 36px;
      height: 36px;
    }

    h1 {
      font-size: 1.75rem;
    }

    .message {
      font-size: 1rem;
    }

    .login-btn {
      padding: 1rem 2rem;
      font-size: 1rem;
    }
  }

  .login-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .error-message {
    color: #ef4444;
    margin-top: 1rem;
    font-size: 0.875rem;
  }
</style>