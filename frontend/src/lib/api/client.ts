import createClient from 'openapi-fetch';
import type { paths } from './schema.d';
import { getLocale, getAuthHeaders, getApiBaseUrl } from './headers';
import { AUTH_TOKEN_KEY } from '$lib/constants';

const _api = createClient<paths>({
  get baseUrl() {
    return getApiBaseUrl();
  },
  headers: {
    get Authorization() {
      const token = localStorage.getItem(AUTH_TOKEN_KEY);
      return token ? `Bearer ${token}` : '';
    },
    get 'Accept-Language'() {
      return getLocale();
    }
  }
});

export const api = _api;

/* ── Raw fetch utilities (auth flows bypass openapi-fetch type system) ── */

export async function rawGet(url: string): Promise<Response> {
  const base = getApiBaseUrl();
  return fetch(base + url, {
    headers: getAuthHeaders()
  });
}

export async function rawPost(url: string, body?: unknown): Promise<Response> {
  const base = getApiBaseUrl();
  return fetch(base + url, {
    method: 'POST',
    headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined
  });
}
