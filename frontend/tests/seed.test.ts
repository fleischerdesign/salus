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
    expect(await db.lab_marker.count()).toBeGreaterThan(0);
    expect(await db.food_item.count()).toBeGreaterThan(0);
    expect(await db.user_metric_preference.count()).toBeGreaterThan(0);

    const steps = await db.metric_definition.get('steps');
    expect(steps?.data_type).toBe('number');
    expect(steps?.source_data_type).toBe('steps');

    const labDefs = await db.metric_definition
      .where('group_key')
      .equals('laboratory')
      .toArray();
    expect(labDefs.length).toBeGreaterThan(0);

    const oats = await db.food_item.get('food-oatmeal');
    expect(oats?.is_verified).toBe(true);
    expect(oats?.user_id).toBeNull();
  });

  it('backfills reference tables for existing installs', async () => {
    await seedReferenceData();
    await db.metric_definition.clear();

    const steps = await db.metric_definition.get('steps');
    expect(steps).toBeUndefined();
    await db.metric_definition.bulkAdd([
      { code: 'steps', name: 'Steps', unit: 'count', data_type: 'number', source_data_type: 'steps', group_key: null, description: null, sort_order: 0, min_value: null, max_value: null }
    ]);
    await db.lab_marker.clear();
    expect(await db.lab_marker.count()).toBe(0);

    await seedReferenceData();

    expect(await db.metric_definition.count()).toBe(1);
    expect(await db.lab_marker.count()).toBeGreaterThan(0);
  });

  it('is idempotent', async () => {
    await seedReferenceData();
    const before = await db.metric_definition.count();

    await seedReferenceData();

    expect(await db.metric_definition.count()).toBe(before);
  });
});
