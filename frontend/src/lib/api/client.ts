import createClient from 'openapi-fetch';
import type { paths } from './schema.d';
import { getLocale, getAuthHeaders } from './headers';

const BASE = typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8000';

const _api = createClient<paths>({
  baseUrl: BASE,
  headers: {
    get Authorization() {
      const token = localStorage.getItem('salus_token');
      return token ? `Bearer ${token}` : '';
    },
    get 'Accept-Language'() {
      return getLocale();
    },
  },
});

export const api = _api;

/* ── Raw fetch utilities (auth flows bypass openapi-fetch type system) ── */

export async function rawGet(url: string): Promise<Response> {
  return fetch(BASE + url, {
    headers: getAuthHeaders(),
    credentials: 'same-origin',
  });
}

export async function rawPost(url: string, body?: unknown): Promise<Response> {
  return fetch(BASE + url, {
    method: 'POST',
    headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
    credentials: 'same-origin',
  });
}
