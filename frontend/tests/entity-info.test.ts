import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createFetchMock } from './helpers/fetch';
import { fetchEntityNames, getEntityNames, resetEntityNames } from '$lib/db/entity-info';

describe('fetchEntityNames', () => {
  beforeEach(() => {
    resetEntityNames();
    vi.clearAllMocks();
  });

  it('returns names from the API and caches them', async () => {
    const fetchMock = createFetchMock([{ body: [{ name: 'measurement' }, { name: 'goal' }] }]);
    vi.stubGlobal('fetch', fetchMock);

    const names = await fetchEntityNames();

    expect(names).toEqual(new Set(['measurement', 'goal']));
    expect(fetchMock).toHaveBeenCalledOnce();

    const cached = await fetchEntityNames();
    expect(fetchMock).toHaveBeenCalledOnce(); // no second fetch
    expect(cached).toEqual(new Set(['measurement', 'goal']));
  });

  it('falls back to hardcoded list on network error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network failure')));

    const names = await fetchEntityNames();

    expect(names).toContain('measurement');
    expect(names).toContain('goal');
  });

  it('falls back to hardcoded list on 500', async () => {
    const fetchMock = createFetchMock([{ status: 500 }]);
    vi.stubGlobal('fetch', fetchMock);

    const names = await fetchEntityNames();

    expect(names).toContain('measurement');
  });

  it('refetches after resetEntityNames', async () => {
    const fetchMock = createFetchMock([
      { body: [{ name: 'measurement' }] },
      { body: [{ name: 'goal' }] }
    ]);
    vi.stubGlobal('fetch', fetchMock);

    await fetchEntityNames();
    resetEntityNames();
    const names = await fetchEntityNames();

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(names).toEqual(new Set(['goal']));
  });

  it('getEntityNames returns hardcoded fallback before first fetch', () => {
    const names = getEntityNames();

    expect(names).toContain('measurement');
    expect(names).toContain('goal');
  });
});
