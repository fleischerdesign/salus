import { Capacitor } from '@capacitor/core';
import { AUTH_TOKEN_KEY, AUTH_USER_KEY } from '$lib/constants';

let _locale = 'en';

if (typeof localStorage !== 'undefined') {
  try {
    const raw = localStorage.getItem(AUTH_USER_KEY);
    if (raw) {
      const user = JSON.parse(raw);
      if (user?.locale) _locale = user.locale;
    }
  } catch {
    /* ignore */
  }
}

export function setLocaleState(locale: string): void {
  _locale = locale;
}

export function getLocale(): string {
  return _locale;
}

export function getApiBaseUrl(): string {
  if (typeof window === 'undefined') return 'http://localhost:8000';
  const custom = localStorage.getItem('salus_server_url');
  if (custom) return custom.replace(/\/+$/, '');
  if (Capacitor.isNativePlatform()) {
    return custom ? custom.replace(/\/+$/, '') : '';
  }
  return window.location.origin;
}

export function setApiBaseUrl(url: string): string {
  let clean = url.trim().replace(/\/+$/, '');
  if (clean && !clean.startsWith('http://') && !clean.startsWith('https://')) {
    clean = `https://${clean}`;
  }
  if (typeof localStorage !== 'undefined') {
    if (clean) {
      localStorage.setItem('salus_server_url', clean);
    } else {
      localStorage.removeItem('salus_server_url');
    }
  }
  return clean;
}

export async function testServerConnection(
  targetUrl: string
): Promise<{ success: boolean; message: string }> {
  let clean = targetUrl.trim().replace(/\/+$/, '');
  if (!clean) return { success: false, message: 'Server URL cannot be empty.' };
  if (!clean.startsWith('http://') && !clean.startsWith('https://')) {
    clean = `https://${clean}`;
  }
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
    const res = await fetch(`${clean}/api/v1/auth/config`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    if (res.ok || res.status === 401) {
      return { success: true, message: 'Connection successful!' };
    }
    return { success: false, message: `Server returned HTTP status ${res.status}` };
  } catch (err: unknown) {
    const errorObj = err as { name?: string };
    if (errorObj?.name === 'AbortError') {
      return { success: false, message: 'Connection timed out after 5 seconds.' };
    }
    return { success: false, message: 'Could not connect to server. Check URL and server status.' };
  }
}

export function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = {
    'Accept-Language': _locale,
    'X-Salus-Sync-Version': '1'
  };
  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (token) headers['Authorization'] = `Bearer ${token}`;
  return headers;
}
