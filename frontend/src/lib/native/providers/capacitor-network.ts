import { Capacitor } from '@capacitor/core';
import { Network } from '@capacitor/network';
import type { INetworkProvider } from '../types';

export class CapacitorNetworkProvider implements INetworkProvider {
  async isOnline(): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return true;
    try {
      const status = await Network.getStatus();
      return status.connected;
    } catch {
      return true;
    }
  }

  onChange(callback: (online: boolean) => void): () => void {
    if (!Capacitor.isNativePlatform()) return () => {};

    let handle: { remove: () => Promise<void> | void } | null = null;
    Network.addListener('networkStatusChange', (status) => callback(status.connected))
      .then((h) => {
        handle = h;
      })
      .catch(() => {});

    return () => {
      handle?.remove();
    };
  }
}
