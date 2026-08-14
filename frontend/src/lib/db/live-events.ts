import { on } from 'svelte/events';
import { AUTH_TOKEN_KEY } from '$lib/constants';

let _eventSource: EventSource | null = null;
let _offSync: (() => void) | null = null;
let _debounceTimer: ReturnType<typeof setTimeout> | null = null;
const DEBOUNCE_MS = 2000;

export function connectLiveSync(onSync: () => void): void {
  disconnectLiveSync();

  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (!token) return;

  _eventSource = new EventSource('/api/v1/sync/events');
  _offSync = on(_eventSource, 'sync', () => {
    if (_debounceTimer) clearTimeout(_debounceTimer);
    _debounceTimer = setTimeout(onSync, DEBOUNCE_MS);
  });
}

export function disconnectLiveSync(): void {
  if (_debounceTimer) {
    clearTimeout(_debounceTimer);
    _debounceTimer = null;
  }
  _offSync?.();
  _offSync = null;
  if (_eventSource) {
    _eventSource.close();
    _eventSource = null;
  }
}
