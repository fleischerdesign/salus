import type { INetworkProvider } from '../types';

export class BrowserNetworkProvider implements INetworkProvider {
  async isOnline(): Promise<boolean> {
    return typeof navigator === 'undefined' ? true : navigator.onLine;
  }

  onChange(callback: (online: boolean) => void): () => void {
    if (typeof window === 'undefined') return () => {};

    const onOnline = () => callback(true);
    const onOffline = () => callback(false);
    window.addEventListener('online', onOnline);
    window.addEventListener('offline', onOffline);

    return () => {
      window.removeEventListener('online', onOnline);
      window.removeEventListener('offline', onOffline);
    };
  }
}
