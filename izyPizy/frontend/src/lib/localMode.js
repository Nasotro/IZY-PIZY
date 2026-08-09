// Local mode detection: the backend reports whether it is running offline
// (no Firebase, no external API keys). The result is cached after the first
// call so every page / apiFetch shares the same answer.
let cached = null;

export const LOCAL_TOKEN = 'local-mode-token';

export async function detectLocalMode() {
  if (cached !== null) return cached;
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 5000);
    const res = await fetch('/api/health', { signal: controller.signal });
    clearTimeout(timer);
    const data = await res.json();
    cached = Boolean(data.local_mode);
  } catch (e) {
    console.warn('Backend unreachable, assuming Firebase mode:', e);
    cached = false;
  }
  return cached;
}
