import { db } from '$lib/db/database';
import { createMeasurements } from '$lib/db/measurement-writes';
import { fetchDailyMeans } from '$lib/db/daily-stats';
import { beforeEach, describe, expect, it } from 'vitest';

function measurement(id: string, metric_code: string, value: number) {
  const now = new Date().toISOString();
  return {
    id,
    user_id: 'u1',
    metric_code,
    source_data_type: 'number',
    source: 'manual',
    value_numeric: value,
    value_text: null,
    value_json: null,
    start_time: now,
    end_time: null,
    notes: null,
    external_id: null,
    created_at: now,
    updated_at: null,
    deleted_at: null
  } as any;
}

beforeEach(async () => {
  await db.delete();
  await db.open();
});

describe('fetchDailyMeans', () => {
  it('returns only the requested metric — no cross-code bleed', async () => {
    await createMeasurements([
      measurement('s1', 'steps', 100),
      measurement('w1', 'weight', 80),
      measurement('h1', 'heart_rate', 60)
    ]);

    const steps = await fetchDailyMeans('steps', '2020-01-01', '2030-01-01');
    expect(steps.length).toBe(1);
    expect(steps[0].mean).toBe(100);

    const weight = await fetchDailyMeans('weight', '2020-01-01', '2030-01-01');
    expect(weight.length).toBe(1);
    expect(weight[0].mean).toBe(80);

    const heart = await fetchDailyMeans('heart_rate', '2020-01-01', '2030-01-01');
    expect(heart.length).toBe(1);
    expect(heart[0].mean).toBe(60);
  });
});
