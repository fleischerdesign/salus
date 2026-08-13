import { describe, it, expect, beforeEach } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { seedReferenceData } from '$lib/db/seed';

describe('seedReferenceData', () => {
  beforeEach(async () => {
    await resetDb();
  });

  it('seeds code-defined reference data into an empty store', async () => {
    await seedReferenceData();

    expect(await db.metric_definition.count()).toBeGreaterThan(0);
    expect(await db.metric_group.count()).toBeGreaterThan(0);
    expect(await db.achievement_definition.count()).toBeGreaterThan(0);
    expect(await db.mood_tag.count()).toBeGreaterThan(0);
    expect(await db.user_metric_preference.count()).toBeGreaterThan(0);

    const steps = await db.metric_definition.get('steps');
    expect(steps?.data_type).toBe('number');
    expect(steps?.source_data_type).toBe('steps');
  });

  it('is idempotent', async () => {
    await seedReferenceData();
    const before = await db.metric_definition.count();

    await seedReferenceData();

    expect(await db.metric_definition.count()).toBe(before);
  });
});
