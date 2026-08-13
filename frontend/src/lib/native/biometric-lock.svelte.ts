import { Capacitor } from '@capacitor/core';
import { nativeBridge } from './bridge';

const BIOMETRIC_KEY = 'salus_biometrics';

class BiometricLockService {
  locked = $state(false);

  private enabled(): boolean {
    return typeof localStorage !== 'undefined' && localStorage.getItem(BIOMETRIC_KEY) === 'true';
  }

  async enforce(): Promise<void> {
    if (!Capacitor.isNativePlatform() || !this.enabled()) return;
    if (!(await nativeBridge.biometric.isAvailable())) return;

    this.locked = true;
    await this.unlock();
  }

  async unlock(): Promise<void> {
    const verified = await nativeBridge.biometric.verifyIdentity('Salus entsperren');
    this.locked = !verified;
  }
}

export const biometricLock = new BiometricLockService();
