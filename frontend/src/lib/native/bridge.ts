import { Capacitor } from '@capacitor/core';
import type { INativeHealthBridge, INotificationProvider } from './types';
import { BrowserHealthBridge } from './providers/browser-health';
import { CapacitorHealthBridge } from './providers/capacitor-health';
import { BrowserNotificationProvider } from './providers/browser-notify';
import { CapacitorNotificationProvider } from './providers/capacitor-notify';

class NativeBridgeFactory {
  private healthBridgeInstance: INativeHealthBridge | null = null;
  private notificationProviderInstance: INotificationProvider | null = null;

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

  get isNative(): boolean {
    return Capacitor.isNativePlatform();
  }
}

export const nativeBridge = new NativeBridgeFactory();
