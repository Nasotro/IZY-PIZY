import { writable } from 'svelte/store';

export const user = writable(null);
export const loading = writable(true);

const LS_KEY = 'izipizy_local_user';

export const LOCAL_USER = {
  uid: 'local-dev',
  email: null,
  displayName: 'Local User',
  photoURL: null,
  local: true,
};

export function loginLocal() {
  localStorage.setItem(LS_KEY, '1');
  user.set(LOCAL_USER);
}

export function logoutLocal() {
  localStorage.removeItem(LS_KEY);
  user.set(null);
}

export function getStoredLocalUser() {
  return localStorage.getItem(LS_KEY) === '1' ? LOCAL_USER : null;
}

export function isLocalUser(u) {
  return Boolean(u && u.local);
}
