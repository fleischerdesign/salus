import { beforeEach, describe, expect, it } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';

describe('notDeleted', () => {
  beforeEach(async () => {
    await resetDb();
    await db.fasting_session.bulkAdd([
      {
        id: 'live-null',
        user_id: 'u',
        started_at: new Date().toISOString(),
        target_hours: 16,
        fasting_type: 'intermittent',
        water_only: true,
        notes: null,
        ended_at: null,
        mood_during: null,
        difficulty: null,
        created_at: new Date().toISOString(),
        updated_at: null,
        deleted_at: null
      },
      {
        id: 'live-empty',
        user_id: 'u',
        started_at: new Date().toISOString(),
        target_hours: 16,
        fasting_type: 'intermittent',
        water_only: true,
        notes: null,
        ended_at: null,
        mood_during: null,
        difficulty: null,
        created_at: new Date().toISOString(),
        updated_at: null,
        deleted_at: ''
      },
      {
        id: 'deleted',
        user_id: 'u',
        started_at: new Date().toISOString(),
        target_hours: 16,
        fasting_type: 'intermittent',
        water_only: true,
        notes: null,
        ended_at: null,
        mood_during: null,
        difficulty: null,
        created_at: new Date().toISOString(),
        updated_at: null,
        deleted_at: '2026-08-14T10:00:00.000Z'
      }
    ]);
  });

  it('includes rows whose deleted_at is null or empty and excludes deleted rows', async () => {
    const rows = await db.notDeleted(db.fasting_session).toArray();
    const ids = rows.map((r) => r.id).sort();
    expect(ids).toEqual(['live-empty', 'live-null']);
  });
});
