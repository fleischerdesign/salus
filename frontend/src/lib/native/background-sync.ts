import { Capacitor } from '@capacitor/core';
import { healthSyncService } from './health-sync.svelte';

/** Device-local background Health Connect sync interval (minutes), configurable in App Settings. */
export const HEALTH_SYNC_INTERVAL_KEY = 'salus_health_sync_interval';
export const HEALTH_SYNC_INTERVAL_DEFAULT_MINUTES = 5;

let _running = false;
let _syncing = false;
let _interval: ReturnType<typeof setInterval> | null = null;
let _visibilityHandler: (() => void) | null = null;

function readIntervalMinutes(): number {
  if (typeof localStorage === 'undefined') return HEALTH_SYNC_INTERVAL_DEFAULT_MINUTES;
  const raw = localStorage.getItem(HEALTH_SYNC_INTERVAL_KEY);
  const parsed = raw ? parseInt(raw, 10) : NaN;
  return Number.isFinite(parsed) && parsed > 0 ? parsed : HEALTH_SYNC_INTERVAL_DEFAULT_MINUTES;
}

export function readBackgroundSyncInterval(): number {
  return readIntervalMinutes();
}

async function backgroundSyncNow(): Promise<void> {
  if (_syncing) return;
  if (!Capacitor.isNativePlatform()) return;
  if (typeof document !== 'undefined' && document.visibilityState !== 'visible') return;
  _syncing = true;
  try {
    await healthSyncService.syncNow();
  } catch (e) {
    console.error('Background health sync failed:', e);
  } finally {
    _syncing = false;
  }
}

function onVisibilityChange(): void {
  if (document.visibilityState === 'visible') void backgroundSyncNow();
}

function restartInterval(): void {
  if (_interval) clearInterval(_interval);
  _interval = setInterval(() => void backgroundSyncNow(), readIntervalMinutes() * 60_000);
}

/**
 * Start the background Health Connect sync: an immediate sync, a periodic sync at the
 * configured interval while the app is visible, and a sync whenever the app returns to the
 * foreground. Returns a cleanup function.
 */
export function startBackgroundSync(): () => void {
  if (_running) return stopBackgroundSync;
  _running = true;
  _visibilityHandler = onVisibilityChange;
  document.addEventListener('visibilitychange', onVisibilityChange);
  restartInterval();
  void backgroundSyncNow();
  return stopBackgroundSync;
}

/** Apply an interval change made in App Settings without restarting the app. */
export function refreshBackgroundSyncInterval(): void {
  if (_running) restartInterval();
}

export function stopBackgroundSync(): void {
  if (_interval) {
    clearInterval(_interval);
    _interval = null;
  }
  if (_visibilityHandler) {
    document.removeEventListener('visibilitychange', _visibilityHandler);
    _visibilityHandler = null;
  }
  _running = false;
}
