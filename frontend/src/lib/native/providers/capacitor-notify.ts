import { LocalNotifications } from '@capacitor/local-notifications';
import type { INotificationProvider, LocalNotificationPayload } from '../types';

export class CapacitorNotificationProvider implements INotificationProvider {
  async requestPermissions(): Promise<boolean> {
    const perm = await LocalNotifications.requestPermissions();
    return perm.display === 'granted';
  }

  async schedule(payload: LocalNotificationPayload): Promise<void> {
    const actionTypeId = payload.actionButtons ? `ACTION_TYPE_${payload.id}` : undefined;

    if (payload.actionButtons && payload.actionButtons.length > 0) {
      await LocalNotifications.registerActionTypes({
        types: [
          {
            id: actionTypeId!,
            actions: payload.actionButtons.map((btn) => ({
              id: btn.id,
              title: btn.title
            }))
          }
        ]
      });
    }

    await LocalNotifications.schedule({
      notifications: [
        {
          id: payload.id,
          title: payload.title,
          body: payload.body,
          schedule: payload.scheduleAt ? { at: payload.scheduleAt } : undefined,
          actionTypeId,
          extra: payload.extraData
        }
      ]
    });
  }

  async cancel(id: number): Promise<void> {
    await LocalNotifications.cancel({
      notifications: [{ id }]
    });
  }
}
