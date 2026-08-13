import { Capacitor } from '@capacitor/core';
import type { INativeHealthBridge, INotificationProvider, IBiometricProvider } from './types';
import { BrowserHealthBridge } from './providers/browser-health';
import { CapacitorHealthBridge } from './providers/capacitor-health';
import { BrowserNotificationProvider } from './providers/browser-notify';
import { CapacitorNotificationProvider } from './providers/capacitor-notify';
import { BrowserBiometricProvider } from './providers/browser-biometric';
import { CapacitorBiometricProvider } from './providers/capacitor-biometric';

class NativeBridgeFactory {
  private healthBridgeInstance: INativeHealthBridge | null = null;
  private notificationProviderInstance: INotificationProvider | null = null;
  private biometricProviderInstance: IBiometricProvider | null = null;

  get health(): INativeHealthBridge {
    if (!this.healthBridgeInstance) {
      this.healthBridgeInstance = Capacitor.isNativePlatform()
        ? new CapacitorHealthBridge()
        : new BrowserHealthBridge();
    }
    return this.healthBridgeInstance;
  }

  get notifications(): INotificationProvider {
    if (!this.notificationProviderInstance) {
      this.notificationProviderInstance = Capacitor.isNativePlatform()
        ? new CapacitorNotificationProvider()
        : new BrowserNotificationProvider();
    }
    return this.notificationProviderInstance;
  }

  get biometric(): IBiometricProvider {
    if (!this.biometricProviderInstance) {
      this.biometricProviderInstance = Capacitor.isNativePlatform()
        ? new CapacitorBiometricProvider()
        : new BrowserBiometricProvider();
    }
    return this.biometricProviderInstance;
  }

  get isNative(): boolean {
    return Capacitor.isNativePlatform();
  }
}

export const nativeBridge = new NativeBridgeFactory();
