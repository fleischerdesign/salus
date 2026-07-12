let _eventSource: EventSource | null = null;
let _debounceTimer: ReturnType<typeof setTimeout> | null = null;
const DEBOUNCE_MS = 2000;

export function connectLiveSync(onSync: () => void): void {
  disconnectLiveSync();

  const token = localStorage.getItem('salus_token');
  if (!token) return;

  _eventSource = new EventSource('/api/v1/sync/events');

  _eventSource.addEventListener('sync', () => {
    if (_debounceTimer) clearTimeout(_debounceTimer);
    _debounceTimer = setTimeout(onSync, DEBOUNCE_MS);
  });
}

export function disconnectLiveSync(): void {
  if (_debounceTimer) {
    clearTimeout(_debounceTimer);
    _debounceTimer = null;
  }
  if (_eventSource) {
    _eventSource.close();
    _eventSource = null;
  }
}
