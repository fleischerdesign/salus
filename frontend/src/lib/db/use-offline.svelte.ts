import { syncEngine } from './sync-engine.svelte';
import { offlineService } from './offline-service';
import { pullDelta } from './sync-pull';
import { connectLiveSync, disconnectLiveSync } from './live-events';

let _online = $state(typeof navigator !== 'undefined' ? navigator.onLine : true);
let _syncing = $state(false);
let _sessionExpired = $state(false);

if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    _online = true;
    syncEngine.flush();
  });
  window.addEventListener('offline', () => {
    _online = false;
  });
}

async function _liveSyncCallback() {
  const last = await (await import('./database')).db.meta.get('lastSyncAt');
  const lastSync = (last?.value as number) ?? 0;
  if (lastSync > 0 && (Date.now() - lastSync) < 7 * 24 * 3600 * 1000) {
    await pullDelta();
  }
}

export const useOffline = {
  get isOnline() {
    return _online;
  },
  get syncing() {
    return _syncing;
  },
  get queueLength() {
    return syncEngine.queueLength;
  },
  get syncError() {
    return syncEngine.error;
  },
  get sessionExpired() {
    return _sessionExpired || syncEngine.sessionExpired;
  },
  retrySync: () => syncEngine.retryFailed(),
  flushSync: () => syncEngine.flush(),
  startLiveSync: () => connectLiveSync(_liveSyncCallback),
  stopLiveSync: () => disconnectLiveSync(),

  async syncAll(): Promise<void> {
    _syncing = true;
    _sessionExpired = false;
    const start = Date.now();

    if ('serviceWorker' in navigator) {
      await navigator.serviceWorker.ready;
    }

    const result = await offlineService.syncAll();
    if (result === 'unauthorized') {
      _sessionExpired = true;
    } else {
      connectLiveSync(_liveSyncCallback);
    }

    const elapsed = Date.now() - start;
    if (elapsed < 1000) {
      await new Promise((r) => setTimeout(r, 1000 - elapsed));
    }
    _syncing = false;
  },
};
