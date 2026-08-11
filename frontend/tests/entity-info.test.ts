import { describe, it, expect, beforeEach, vi } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { createFetchMock } from './helpers/fetch';
import { fetchEntityNames, getEntityNames, resetEntityNames } from '$lib/db/entity-info';

describe('fetchEntityNames', () => {
  beforeEach(async () => {
    await resetDb();
    resetEntityNames();
    vi.clearAllMocks();
  });

  it('returns names from the API and caches them', async () => {
    const fetchMock = createFetchMock([{ body: { entities: [{ name: 'measurement' }, { name: 'goal' }], commands: [] } }]);
    vi.stubGlobal('fetch', fetchMock);

    const names = await fetchEntityNames();

    expect(names).toEqual(new Set(['measurement', 'goal']));
    expect(fetchMock).toHaveBeenCalledOnce();

    const cached = await fetchEntityNames();
    expect(fetchMock).toHaveBeenCalledOnce(); // no second fetch
    expect(cached).toEqual(new Set(['measurement', 'goal']));
  });

  it('falls back to cached list in Dexie on network error', async () => {
    await db.meta.put({ key: 'sync:entity_names', value: ['measurement', 'goal'] });
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network failure')));

    const names = await fetchEntityNames();

    expect(names).toContain('measurement');
    expect(names).toContain('goal');
  });

  it('falls back to cached list in Dexie on 500', async () => {
    await db.meta.put({ key: 'sync:entity_names', value: ['measurement'] });
    const fetchMock = createFetchMock([{ status: 500 }]);
    vi.stubGlobal('fetch', fetchMock);

    const names = await fetchEntityNames();

    expect(names).toContain('measurement');
  });

  it('refetches after resetEntityNames', async () => {
    const fetchMock = createFetchMock([
      { body: { entities: [{ name: 'measurement' }], commands: [] } },
      { body: { entities: [{ name: 'goal' }], commands: [] } }
    ]);
    vi.stubGlobal('fetch', fetchMock);

    await fetchEntityNames();
    resetEntityNames();
    const names = await fetchEntityNames();

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(names).toEqual(new Set(['goal']));
  });

  it('getEntityNames returns empty set before first fetch', () => {
    const names = getEntityNames();

    expect(names).toEqual(new Set());
  });
});
