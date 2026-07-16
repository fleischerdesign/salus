import { rawGet } from '$lib/api/client';

let oidcProviders = $state<string[]>([]);
let loaded = $state(false);

export const authConfig = {
  get oidcProviders() {
    return oidcProviders;
  },
  get loaded() {
    return loaded;
  },
  async load() {
    if (loaded) return;
    try {
      const res = await rawGet('/api/v1/auth/config');
      if (res.ok) {
        const data = await res.json();
        oidcProviders = data.oidc_providers || [];
        loaded = true;
      }
    } catch (e) {
      console.error('Failed to load auth configuration:', e);
    }
  }
};
