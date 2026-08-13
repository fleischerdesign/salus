import { describe, it, expect, beforeEach } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { seedReferenceData } from '$lib/db/seed';
import { evaluateLocalAchievements } from '$lib/db/local-achievements';

function addMeasurement(id: string) {
  return db.measurement.put({
    id,
    user_id: 'self',
    metric_code: 'steps',
    source_data_type: 'steps',
    source: 'manual',
    value_numeric: 100,
    value_text: null,
    value_json: null,
    start_time: '2026-08-13T10:00:00Z',
    end_time: null,
    notes: null,
    external_id: null,
    created_at: '2026-08-13T10:00:00Z',
    updated_at: null,
    deleted_at: null
  });
}

describe('evaluateLocalAchievements', () => {
  beforeEach(async () => {
    await resetDb();
    await seedReferenceData();
  });

  it('unlocks first_entry after one measurement', async () => {
    await addMeasurement('m1');

    const unlocked = await evaluateLocalAchievements();

    expect(unlocked.has('first_entry')).toBe(true);
  });

  it('does not unlock entries_10 with fewer than 10 measurements', async () => {
    for (let i = 0; i < 5; i++) await addMeasurement(`m${i}`);

    const unlocked = await evaluateLocalAchievements();

    expect(unlocked.has('first_entry')).toBe(true);
    expect(unlocked.has('entries_10')).toBe(false);
  });

  it('unlocks entries_10 with 10 measurements', async () => {
    for (let i = 0; i < 10; i++) await addMeasurement(`m${i}`);

    const unlocked = await evaluateLocalAchievements();

    expect(unlocked.has('entries_10')).toBe(true);
  });

  it('never unlocks the server-only sharing achievement', async () => {
    await addMeasurement('m1');

    const unlocked = await evaluateLocalAchievements();

    expect(unlocked.has('first_share')).toBe(false);
  });
});
