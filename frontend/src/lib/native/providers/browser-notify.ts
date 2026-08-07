import type { INotificationProvider, LocalNotificationPayload } from '../types';

export class BrowserNotificationProvider implements INotificationProvider {
  async requestPermissions(): Promise<boolean> {
    if (typeof window === 'undefined' || !('Notification' in window)) return false;
    const result = await Notification.requestPermission();
    return result === 'granted';
  }

  async schedule(payload: LocalNotificationPayload): Promise<void> {
    if (typeof window === 'undefined' || !('Notification' in window)) return;
    if (Notification.permission === 'granted') {
      new Notification(payload.title, {
        body: payload.body
      });
    }
  }

  async cancel(_id: number): Promise<void> {
    // Web notifications do not support cancelling past scheduled instances directly
  }
}
