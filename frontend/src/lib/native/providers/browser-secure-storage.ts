import type { ISecureStorageProvider } from '../types';

export class BrowserSecureStorageProvider implements ISecureStorageProvider {
  async setToken(_token: string): Promise<void> {}

  async setServerUrl(_url: string): Promise<void> {}

  async clear(): Promise<void> {}
}
