import { render, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import NotificationBell from '$lib/components/feedback/NotificationBell.svelte';
import { db } from '$lib/db/database';
import { resetDb } from '../helpers/db';

vi.mock('$lib/mutations/notification', () => ({
  markAllNotificationsRead: vi.fn()
}));

async function seedNotifications() {
  await db.notification.bulkAdd([
    {
      id: 'n1',
      user_id: 'u',
      title: 'Unusual data detected',
      message: 'steps deviated',
      is_read: false,
      category: 'data_quality',
      severity: 'warning',
      link: '/entries/steps',
      created_at: new Date().toISOString(),
      updated_at: null,
      deleted_at: null
    },
    {
      id: 'n2',
      user_id: 'u',
      title: 'Welcome',
      message: 'Hello',
      is_read: false,
      category: 'system',
      severity: 'info',
      link: null,
      created_at: new Date().toISOString(),
      updated_at: null,
      deleted_at: null
    }
  ]);
}

beforeEach(async () => {
  await resetDb();
});

describe('NotificationBell', () => {
  it('renders an anchor for notifications with a link', async () => {
    await seedNotifications();
    const { container } = render(NotificationBell);
    await waitFor(() => {
      expect(container.querySelector('a[href="/entries/steps"]')).not.toBeNull();
    });
  });

  it('does not render an anchor for notifications without a link', async () => {
    await seedNotifications();
    const { container } = render(NotificationBell);
    await waitFor(() => {
      expect(container.querySelectorAll('a[href^="/entries/"]').length).toBe(1);
    });
  });

  it('pulses the unread dot for critical notifications', async () => {
    await db.notification.add({
      id: 'n3',
      user_id: 'u',
      title: 'Security',
      message: 'x',
      is_read: false,
      category: 'system',
      severity: 'critical',
      link: null,
      created_at: new Date().toISOString(),
      updated_at: null,
      deleted_at: null
    });
    const { container } = render(NotificationBell);
    await waitFor(() => {
      expect(container.querySelector('.animate-pulse.bg-error-500')).not.toBeNull();
    });
  });
});
