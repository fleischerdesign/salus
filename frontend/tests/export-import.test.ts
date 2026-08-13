import { describe, it, expect, beforeEach } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { seedReferenceData } from '$lib/db/seed';
import { exportDatabase, importDatabase } from '$lib/db/export-import';

describe('export/import', () => {
  beforeEach(async () => {
    await resetDb();
  });

  it('round-trips the store', async () => {
    await seedReferenceData();
    await db.measurement.put({
      id: 'm1',
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

    const json = await exportDatabase();
    await resetDb();

    expect(await db.measurement.count()).toBe(0);
    expect(await db.metric_definition.count()).toBe(0);

    await importDatabase(json);

    expect(await db.measurement.count()).toBe(1);
    expect(await db.metric_definition.count()).toBeGreaterThan(0);
  });

  it('rejects invalid JSON', async () => {
    await expect(importDatabase('not json')).rejects.toThrow();
  });

  it('rejects JSON without a data map', async () => {
    await expect(importDatabase(JSON.stringify({ version: 1 }))).rejects.toThrow();
  });
});
