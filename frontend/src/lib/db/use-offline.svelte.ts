import { syncEngine } from './sync-engine.svelte';
import { offlineService } from './offline-service';
import { pullDelta } from './sync-pull';
import { connectLiveSync, disconnectLiveSync } from './live-events';
import { db } from './database';
import { network } from '$lib/native/network';
import { localMode } from './local-mode.svelte';
import { toast, dismissToast, updateToastProgress } from '$components/ui/toast-state.svelte';
import { toastSettings } from '$stores/toast-settings.svelte';
import { Capacitor } from '@capacitor/core';

let _sessionExpired = $state(false);
let _syncToastId: number | null = null;
let _wasOffline = !network.isOnline;

network.subscribe((online) => {
  if (online) {
    if (_wasOffline && toastSettings.networkStatus) {
      toast('Connection restored.', 'success', { duration: 4000 });
    }
    _wasOffline = false;
    syncEngine.flush();
  } else {
    _wasOffline = true;
    if (toastSettings.networkStatus) {
      toast('You are offline. Changes sync when reconnected.', 'warning', { duration: 4000 });
    }
  }
});

async function _liveSyncCallback() {
  const last = await db.meta.get('lastSyncAt');
  const lastSync = (last?.value as number) ?? 0;
  if (lastSync > 0 && Date.now() - lastSync < 7 * 24 * 3600 * 1000) {
    await pullDelta();
  }
}

export interface SyncAllOptions {
  manual?: boolean;
  silent?: boolean;
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

  async syncAll(opts: SyncAllOptions = {}): Promise<void> {
    if (localMode.active) return;

    if (_syncToastId !== null) {
      dismissToast(_syncToastId);
      _syncToastId = null;
    }

    _sessionExpired = false;

    const showToasts = opts.silent
      ? false
      : opts.manual
        ? toastSettings.manualSync
        : toastSettings.backgroundSync;

    if (showToasts) {
      _syncToastId = toast('Connecting...', 'loading', { persistent: true, progress: true });
    }

    const onProgress = (message: string, progress?: number) => {
      if (_syncToastId !== null) {
        updateToastProgress(_syncToastId, message, progress ?? 0);
      }
    };

    if (!Capacitor.isNativePlatform() && 'serviceWorker' in navigator) {
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
      if (showToasts || (opts.manual && toastSettings.manualSync)) {
        toast('You are offline. Sync skipped.', 'warning', { duration: 4000 });
      }
    } else {
      connectLiveSync(_liveSyncCallback);
      if (showToasts) {
        toast('Sync complete.', 'success', { duration: 3000 });
      }
    }
  }
};
