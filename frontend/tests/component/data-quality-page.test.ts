import { render, waitFor } from '@testing-library/svelte';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import DataQualityPage from '../../src/routes/settings/data-quality/+page.svelte';
import { db } from '$lib/db/database';
import { resetDb } from '../helpers/db';

vi.mock('$lib/mutations/data-quality', () => ({
  runDataQualityCheck: vi.fn(() => Promise.resolve({ ok: true })),
  acknowledgeDataQualityFlag: vi.fn(() => Promise.resolve({ ok: true }))
}));

vi.mock('$lib/mutations/account', () => ({
  updateProfile: vi.fn(() => Promise.resolve({ ok: true }))
}));

beforeEach(async () => {
  await resetDb();
  await db.metric_definition.add({
    code: 'steps',
    name: 'Steps',
    unit: 'steps',
    data_type: 'number',
    source_data_type: 'steps',
    group_key: null,
    description: null,
    sort_order: 10,
    min_value: 0,
    max_value: 150000
  });
  await db.user_profile.add({
    id: 'u',
    username: 'alice',
    email: null,
    display_name: null,
    theme: 'system',
    locale: 'en',
    timezone: 'UTC',
    colorblind: false,
    accent_hue: null,
    onboarding_dismissed: false,
    dq_notify_hard_bound: true,
    dq_notify_cross_source: true,
    dq_notify_anomaly: true,
    is_admin: false,
    is_active: true,
    created_at: null
  });
  await db.data_quality_flag.add({
    id: 'f1',
    user_id: 'u',
    kind: 'hard_bound',
    metric_code: 'steps',
    measurement_id: 'm1',
    severity: 'warning',
    message: 'Steps value 999999 is above plausible maximum 150000',
    context_json: null,
    resolved_at: null,
    created_at: new Date().toISOString(),
    updated_at: null
  });
});

describe('DataQuality settings page', () => {
  it('renders findings with a metric name and acknowledge button', async () => {
    const { container } = render(DataQualityPage);
    await waitFor(() => {
      expect(container.textContent).toContain('Steps');
      expect(container.textContent).toContain('above plausible maximum');
      expect(container.textContent).toContain('Als gesehen');
    });
  });

  it('renders the notification toggles', async () => {
    const { container } = render(DataQualityPage);
    await waitFor(() => {
      expect(container.textContent).toContain('Hard-bound alerts');
      expect(container.textContent).toContain('Cross-source alerts');
      expect(container.textContent).toContain('Anomaly alerts');
    });
  });
});
