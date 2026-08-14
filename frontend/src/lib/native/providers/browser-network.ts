import { on } from 'svelte/events';
import type { INetworkProvider } from '../types';

export class BrowserNetworkProvider implements INetworkProvider {
  async isOnline(): Promise<boolean> {
    return typeof navigator === 'undefined' ? true : navigator.onLine;
  }

  onChange(callback: (online: boolean) => void): () => void {
    if (typeof window === 'undefined') return () => {};

    const offOnline = on(window, 'online', () => callback(true));
    const offOffline = on(window, 'offline', () => callback(false));

    return () => {
      offOnline();
      offOffline();
    };
  }
}
