import type { components } from '$lib/api/schema.d';
import { setLocaleState, getApiBaseUrl } from '$lib/api/headers';
import { AUTH_TOKEN_KEY, AUTH_USER_KEY, SELF_USER_ID } from '$lib/constants';
import { nativeBridge } from '$lib/native/bridge';
import { localMode } from '$lib/db/local-mode.svelte';

type User = components['schemas']['UserResponse'];

const LOCAL_TOKEN = 'local';

function buildLocalUser(displayName: string): User {
  const now = new Date().toISOString();
  return {
    id: SELF_USER_ID,
    username: displayName,
    display_name: displayName,
    email: null,
    height_cm: null,
    is_active: true,
    is_admin: false,
    locale: 'en',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    colorblind: false,
    accent_hue: null,
    onboarding_dismissed: false,
    theme: 'system',
    created_at: now,
    updated_at: now
  };
}

interface AuthState {
  token: string | null;
  user: User | null;
  loading: boolean;
}

function loadUser(): User | null {
  if (typeof localStorage === 'undefined') return null;
  try {
    const raw = localStorage.getItem(AUTH_USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

const state = $state<AuthState>({
  token: typeof localStorage !== 'undefined' ? localStorage.getItem(AUTH_TOKEN_KEY) : null,
  user: loadUser(),
  loading: typeof localStorage !== 'undefined' && !!localStorage.getItem(AUTH_TOKEN_KEY)
});

export const auth = {
  get token() {
    return state.token;
  },
  get user() {
    return state.user;
  },
  get loading() {
    return state.loading;
  },
  get isAuthenticated() {
    return state.token !== null && state.user !== null;
  },
  get isAdmin() {
    return state.user?.is_admin ?? false;
  },

  setSession(token: string, user: User) {
    localMode.disable();
    state.token = token;
    state.user = user;
    state.loading = false;
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
    setLocaleState(user.locale ?? 'en');
    nativeBridge.secureStorage.setToken(token).catch(() => {});
    nativeBridge.secureStorage.setServerUrl(getApiBaseUrl()).catch(() => {});
  },

  setLocalSession(displayName: string) {
    const user = buildLocalUser(displayName);
    state.token = LOCAL_TOKEN;
    state.user = user;
    state.loading = false;
    localStorage.setItem(AUTH_TOKEN_KEY, LOCAL_TOKEN);
    localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
    setLocaleState(user.locale ?? 'en');
    localMode.enable();
  },

  clear() {
    state.token = null;
    state.user = null;
    state.loading = false;
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
    nativeBridge.secureStorage.clear().catch(() => {});
  },

  setLoading(loading: boolean) {
    state.loading = loading;
  }
};

export { type User };
