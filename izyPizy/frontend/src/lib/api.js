import { getIdToken } from "firebase/auth";
import { auth } from "./firebase.js";
import { detectLocalMode, LOCAL_TOKEN } from "./localMode.js";

const BASE = '/api';

export let currentToken = null;

export async function apiFetch(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  
  if (await detectLocalMode()) {
    // Local mode: no Firebase, just send the local token.
    headers['Authorization'] = `Bearer ${LOCAL_TOKEN}`;
  } else if (auth.currentUser) {
    try {
      const token = await getIdToken(auth.currentUser);
      currentToken = token;
      headers['Authorization'] = `Bearer ${token}`;
    } catch (e) {
      console.warn('Failed to get token:', e);
    }
  }

  const res = await fetch(`${BASE}${path}`, {
    headers,
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

// Pi
export const getPi = (start = 0, length = 10) =>
  apiFetch(`/pi?start=${start}&length=${length}`);

// Dictionary
export const getDictionary = () => apiFetch('/dictionary');

export const addWord = (number, word) =>
  apiFetch(`/dictionary/${number}/words`, {
    method: 'POST',
    body: JSON.stringify({ word }),
  });

export const updateWord = (wordId, word) =>
  apiFetch(`/dictionary/words/${wordId}`, {
    method: 'PUT',
    body: JSON.stringify({ word }),
  });

export const deleteWord = (wordId) =>
  apiFetch(`/dictionary/words/${wordId}`, { method: 'DELETE' });

// Stories
export const getStories = (position = null) => {
  const query = position !== null ? `?position=${position}` : '';
  return apiFetch(`/stories${query}`);
};

export const createStory = (data) =>
  apiFetch('/stories', {
    method: 'POST',
    body: JSON.stringify(data),
  });

export const updateStory = (storyId, data) =>
  apiFetch(`/stories/${storyId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });

export const deleteStory = (storyId) =>
  apiFetch(`/stories/${storyId}`, { method: 'DELETE' });

// NEW: Generate image for a story
export const generateStoryImage = (storyId) =>
  apiFetch(`/stories/${storyId}/generate-image`, {
    method: 'POST',
  });

// NEW: Generate multiple images for a story with custom options
export const generateStoryImageBatch = (storyId, options = {}) =>
  apiFetch(`/stories/${storyId}/generate-image-batch`, {
    method: 'POST',
    body: JSON.stringify(options),
  });

// NEW: Get enhanced prompt preview
export const getEnhancedPromptPreview = (prompt, keyElements = null) =>
  apiFetch('/stories/preview-prompt', {
    method: 'POST',
    body: JSON.stringify({ prompt, key_elements: keyElements }),
  });

// NEW: Set the image for a story (used after batch generation)
export const setStoryImage = (storyId, imagePath) =>
  apiFetch(`/stories/${storyId}/set-image`, {
    method: 'POST',
    body: JSON.stringify({ image_path: imagePath }),
  });

// NEW: Get image URL for display
export const getImageUrl = (imagePath) => {
  if (!imagePath) return null;
  return `/api/images/${imagePath}`;
};

// Training
export const verifyDigit = (position, digit) =>
  apiFetch('/train/verify', {
    method: 'POST',
    body: JSON.stringify({ position, digit }),
  });
