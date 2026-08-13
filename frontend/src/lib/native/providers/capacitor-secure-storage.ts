import { Capacitor, registerPlugin } from '@capacitor/core';
import type { ISecureStorageProvider } from '../types';

interface SecureStoragePluginNative {
  setToken(options: { token: string }): Promise<void>;
  setServerUrl(options: { url: string }): Promise<void>;
  clear(): Promise<void>;
}

const SecureStorageNative = registerPlugin<SecureStoragePluginNative>('SecureStoragePlugin');

export class CapacitorSecureStorageProvider implements ISecureStorageProvider {
  async setToken(token: string): Promise<void> {
    if (!Capacitor.isNativePlatform()) return;
    try {
      await SecureStorageNative.setToken({ token });
    } catch {
      /* ignore */
    }
  }

  async setServerUrl(url: string): Promise<void> {
    if (!Capacitor.isNativePlatform()) return;
    try {
      await SecureStorageNative.setServerUrl({ url });
    } catch {
      /* ignore */
    }
  }

  async clear(): Promise<void> {
    if (!Capacitor.isNativePlatform()) return;
    try {
      await SecureStorageNative.clear();
    } catch {
      /* ignore */
    }
  }
}
