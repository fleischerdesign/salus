import { db } from '$lib/db/database';
import { fetchTrend } from '$lib/analytics/views/analytics';
import { createMeasurements } from '$lib/db/measurement-writes';
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
  };
}

beforeEach(async () => {
  await db.delete();
  await db.open();
});

describe('fetchTrend', () => {
  it('queries by metric_code — not by the DataType enum value', async () => {
    await createMeasurements([
      measurement('m1', 'steps', 100),
      measurement('m2', 'steps', 120),
      measurement('m3', 'steps', 140)
    ]);

    const byCode = await fetchTrend('steps', '7d');
    expect(byCode.values.length).toBeGreaterThan(0);

    const byDataType = await fetchTrend('number', '7d');
    expect(byDataType.values).toEqual([]);
  });
});
