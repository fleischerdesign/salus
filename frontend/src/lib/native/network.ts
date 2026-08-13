import { Capacitor } from '@capacitor/core';
import type { INetworkProvider } from './types';
import { BrowserNetworkProvider } from './providers/browser-network';
import { CapacitorNetworkProvider } from './providers/capacitor-network';

const provider: INetworkProvider = Capacitor.isNativePlatform()
  ? new CapacitorNetworkProvider()
  : new BrowserNetworkProvider();

let _online = typeof navigator === 'undefined' ? true : navigator.onLine;
let _initialized = false;
const _listeners = new Set<(online: boolean) => void>();

function emit(online: boolean): void {
  if (_online === online) return;
  _online = online;
  for (const callback of [..._listeners]) callback(online);
}

function init(): void {
  if (_initialized) return;
  _initialized = true;
  provider.onChange(emit);
  if (Capacitor.isNativePlatform()) {
    provider
      .isOnline()
      .then(emit)
      .catch(() => {});
  }
}

export const network = {
  get isOnline(): boolean {
    if (Capacitor.isNativePlatform()) return _online;
    return typeof navigator === 'undefined' ? true : navigator.onLine;
  },

  subscribe(callback: (online: boolean) => void): () => void {
    init();
    _listeners.add(callback);
    return () => {
      _listeners.delete(callback);
    };
  }
};
