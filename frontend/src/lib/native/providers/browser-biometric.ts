import type { IBiometricProvider } from '../types';

export class BrowserBiometricProvider implements IBiometricProvider {
  async isAvailable(): Promise<boolean> {
    return false;
  }

  async verifyIdentity(_reason: string): Promise<boolean> {
    return false;
  }
}
