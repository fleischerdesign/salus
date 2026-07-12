import type { components } from '$lib/api/schema.d';
import { setLocaleState } from '$lib/api/headers';

type User = components['schemas']['UserResponse'];

interface AuthState {
  token: string | null;
  user: User | null;
  loading: boolean;
}

function loadUser(): User | null {
  if (typeof localStorage === 'undefined') return null;
  try {
    const raw = localStorage.getItem('salus_user');
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

const state = $state<AuthState>({
  token: typeof localStorage !== 'undefined' ? localStorage.getItem('salus_token') : null,
  user: loadUser(),
  loading: typeof localStorage !== 'undefined' && !!localStorage.getItem('salus_token')
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
    state.token = token;
    state.user = user;
    state.loading = false;
    localStorage.setItem('salus_token', token);
    localStorage.setItem('salus_user', JSON.stringify(user));
    setLocaleState(user.locale ?? 'en');
  },

  clear() {
    state.token = null;
    state.user = null;
    state.loading = false;
    localStorage.removeItem('salus_token');
    localStorage.removeItem('salus_user');
  },

  setLoading(loading: boolean) {
    state.loading = loading;
  }
};

export { type User };
