import { Capacitor } from '@capacitor/core';
import { BiometricAuth } from '@aparajita/capacitor-biometric-auth';
import type { IBiometricProvider } from '../types';

export class CapacitorBiometricProvider implements IBiometricProvider {
  async isAvailable(): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false;
    try {
      const res = await BiometricAuth.checkBiometry();
      return res.isAvailable;
    } catch {
      return false;
    }
  }

  async verifyIdentity(reason: string): Promise<boolean> {
    if (!Capacitor.isNativePlatform()) return false;
    try {
      await BiometricAuth.authenticate({ reason, cancelTitle: 'Abbrechen' });
      return true;
    } catch {
      return false;
    }
  }
}
