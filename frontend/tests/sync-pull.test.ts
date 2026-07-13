import { describe, it, expect, beforeEach, vi } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { createFetchMock } from './helpers/fetch';
import { pullFull, pullDelta } from '$lib/db/sync-pull';

vi.mock('$lib/db/entity-info', () => ({
  fetchEntityNames: vi.fn().mockResolvedValue(new Set(['measurement', 'goal'])),
  resetEntityNames: vi.fn()
}));

describe('pullFull', () => {
  beforeEach(async () => {
    await resetDb();
    vi.clearAllMocks();
  });

  it('loads a single batch into the database', async () => {
    const fetchMock = createFetchMock([
      {
        body: {
          cursors: { measurement: 100, goal: 50 },
          has_more: false,
          synced_at: '2026-07-13T12:00:00Z',
          measurement: [{ id: 1, data_type: 'weight', value_numeric: 75 }],
          goal: [{ id: 1, target_value: 100, metric_type_id: 1 }]
        }
      }
    ]);
    vi.stubGlobal('fetch', fetchMock);

    const result = await pullFull();

    expect(result).toBe(true);
    const measurements = await db.measurement.toArray();
    expect(measurements).toHaveLength(1);
    expect(measurements[0].data_type).toBe('weight');

    const goals = await db.goal.toArray();
    expect(goals).toHaveLength(1);
    expect(goals[0].target_value).toBe(100);

    const meta = await db.meta.get('lastSyncAt');
    expect(meta).toBeDefined();
    expect(meta!.value).toBe(new Date('2026-07-13T12:00:00Z').getTime());
  });

  it('loads multiple batches via cursor pagination', async () => {
    const fetchMock = createFetchMock([
      {
        body: {
          cursors: { measurement: 50 },
          has_more: true,
          synced_at: '2026-07-13T12:00:00Z',
          measurement: [{ id: 1, data_type: 'weight' }]
        }
      },
      {
        body: {
          cursors: { measurement: 100 },
          has_more: false,
          synced_at: '2026-07-13T12:00:00Z',
          measurement: [{ id: 2, data_type: 'steps' }]
        }
      }
    ]);
    vi.stubGlobal('fetch', fetchMock);

    const result = await pullFull();

    expect(result).toBe(true);
    expect(fetchMock).toHaveBeenCalledTimes(2);
    const measurements = await db.measurement.toArray();
    expect(measurements).toHaveLength(2);
  });

  it('skips meta keys (cursors, has_more, synced_at) when saving', async () => {
    const fetchMock = createFetchMock([
      {
        body: {
          cursors: { measurement: 100 },
          has_more: false,
          synced_at: '2026-07-13T12:00:00Z',
          measurement: [{ id: 1, data_type: 'weight' }]
        }
      }
    ]);
    vi.stubGlobal('fetch', fetchMock);

    await pullFull();

    const tables = await db.tables.map((t) => t.name);
    expect(tables).not.toContain('cursors');
    expect(tables).not.toContain('has_more');
    expect(tables).not.toContain('synced_at');
  });

  it('ignores tables not in entity names', async () => {
    const fetchMock = createFetchMock([
      {
        body: {
          cursors: {},
          has_more: false,
          synced_at: '2026-07-13T12:00:00Z',
          measurement: [{ id: 1, data_type: 'weight' }],
          unknown_table: [{ id: 99 }]
        }
      }
    ]);
    vi.stubGlobal('fetch', fetchMock);

    const result = await pullFull();

    expect(result).toBe(true);
    const measurements = await db.measurement.toArray();
    expect(measurements).toHaveLength(1);
  });

  it('returns unauthorized on 401', async () => {
    const fetchMock = createFetchMock([{ status: 401 }]);
    vi.stubGlobal('fetch', fetchMock);

    const result = await pullFull();
    expect(result).toBe('unauthorized');
  });

  it('returns false on network error', async () => {
    const fetchMock = vi.fn().mockRejectedValue(new Error('Network failure'));
    vi.stubGlobal('fetch', fetchMock);

    const result = await pullFull();
    expect(result).toBe(false);
  });
});

describe('pullDelta', () => {
  beforeEach(async () => {
    await resetDb();
    vi.clearAllMocks();
    await db.meta.put({ key: 'lastSyncAt', value: new Date('2026-07-12T00:00:00Z').getTime() });
  });

  it('applies changed rows', async () => {
    const fetchMock = createFetchMock([
      {
        body: {
          changed: { measurement: [{ id: 10, data_type: 'weight' }] },
          deleted: {},
          synced_at: '2026-07-13T12:00:00Z'
        }
      }
    ]);
    vi.stubGlobal('fetch', fetchMock);

    const result = await pullDelta();

    expect(result).toBe(true);
    const measurements = await db.measurement.toArray();
    expect(measurements).toHaveLength(1);
    expect(measurements[0].id).toBe(10);
  });

  it('applies deleted rows', async () => {
    await db.table('measurement').put({
      id: 5,
      data_type: 'heart_rate',
      user_id: 1,
      metric_type_id: 1,
      source: 'test',
      value_numeric: null,
      value_text: null,
      value_json: null,
      start_time: '',
      end_time: null,
      notes: null,
      external_id: null,
      created_at: '',
      updated_at: null,
      deleted_at: null
    });

    const fetchMock = createFetchMock([
      {
        body: {
          changed: {},
          deleted: { measurement: [5] },
          synced_at: '2026-07-13T12:00:00Z'
        }
      }
    ]);
    vi.stubGlobal('fetch', fetchMock);

    await pullDelta();

    const measurements = await db.measurement.toArray();
    expect(measurements).toHaveLength(0);
  });

  it('updates lastSyncAt after success', async () => {
    const fetchMock = createFetchMock([
      {
        body: {
          changed: {},
          deleted: {},
          synced_at: '2026-07-13T12:00:00Z'
        }
      }
    ]);
    vi.stubGlobal('fetch', fetchMock);

    await pullDelta();

    const meta = await db.meta.get('lastSyncAt');
    expect(meta).toBeDefined();
    expect(meta!.value).toBe(new Date('2026-07-13T12:00:00Z').getTime());
  });

  it('ignores tables not in entity names', async () => {
    const fetchMock = createFetchMock([
      {
        body: {
          changed: { unknown_table: [{ id: 99 }] },
          deleted: {},
          synced_at: '2026-07-13T12:00:00Z'
        }
      }
    ]);
    vi.stubGlobal('fetch', fetchMock);

    const result = await pullDelta();
    expect(result).toBe(true);
  });
  it('returns unauthorized on 401', async () => {
    const fetchMock = createFetchMock([{ status: 401 }]);
    vi.stubGlobal('fetch', fetchMock);

    const result = await pullDelta();
    expect(result).toBe('unauthorized');
  });
  it('returns false on network error', async () => {
    const fetchMock = vi.fn().mockRejectedValue(new Error('Network failure'));
    vi.stubGlobal('fetch', fetchMock);

    const result = await pullDelta();
    expect(result).toBe(false);
  });
});
