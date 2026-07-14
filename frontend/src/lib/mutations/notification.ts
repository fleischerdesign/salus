import { mutate } from '$lib/mutate';

export const markNotificationRead = (notificationId: string) =>
  mutate({
    kind: 'command',
    command: 'mark_notification_read',
    queueable: false,
    payload: { id: notificationId }
  });

export const markAllNotificationsRead = () =>
  mutate({
    kind: 'command',
    command: 'mark_all_notifications_read',
    queueable: false,
    payload: {}
  });
