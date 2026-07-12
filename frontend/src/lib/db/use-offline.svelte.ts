import { syncEngine } from './sync-engine.svelte';
import { offlineService } from './offline-service';
import { pullDelta } from './sync-pull';
import { connectLiveSync, disconnectLiveSync } from './live-events';
import { toast, dismissToast, updateToast } from '$components/ui/toast-state.svelte';

let _online = $state(typeof navigator !== 'undefined' ? navigator.onLine : true);
let _sessionExpired = $state(false);
let _syncToastId: number | null = null;
let _wasOffline = !_online;

if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    _online = true;
    if (_wasOffline) {
      toast('Connection restored.', 'success', { duration: 4000 });
    }
    _wasOffline = false;
    syncEngine.flush();
  });
  window.addEventListener('offline', () => {
    _online = false;
    _wasOffline = true;
    toast('You are offline. Changes sync when reconnected.', 'warning', { duration: 4000 });
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
  get queueLength() {
    return syncEngine.queueLength;
  },
  get sessionExpired() {
    return _sessionExpired || syncEngine.sessionExpired;
  },
  retrySync: () => syncEngine.retryFailed(),
  flushSync: () => syncEngine.flush(),
  startLiveSync: () => connectLiveSync(_liveSyncCallback),
  stopLiveSync: () => disconnectLiveSync(),

  async syncAll(): Promise<void> {
    if (_syncToastId !== null) {
      dismissToast(_syncToastId);
    }

    _sessionExpired = false;
    _syncToastId = toast('Connecting...', 'loading', { persistent: true, progress: true });

    const onProgress = (message: string) => {
      if (_syncToastId !== null) {
        updateToast(_syncToastId, message);
      }
    };

    if ('serviceWorker' in navigator) {
      await navigator.serviceWorker.ready;
    }

    const result = await offlineService.syncAll(onProgress);

    if (_syncToastId !== null) {
      dismissToast(_syncToastId);
      _syncToastId = null;
    }

    if (result === 'unauthorized') {
      _sessionExpired = true;
      toast('Session expired. Please log in again.', 'error');
    } else if (result === false) {
      toast('You are offline. Sync skipped.', 'warning', { duration: 4000 });
    } else {
      connectLiveSync(_liveSyncCallback);
      toast('Sync complete.', 'success', { duration: 3000 });
    }
  },
};
