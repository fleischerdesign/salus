import { describe, it, expect, beforeEach, vi } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { offlineService } from '$lib/db/offline-service';

const { mockPullFull, mockPullDelta } = vi.hoisted(() => ({
  mockPullFull: vi.fn(),
  mockPullDelta: vi.fn()
}));

vi.mock('$lib/db/sync-pull', () => ({
  pullFull: mockPullFull,
  pullDelta: mockPullDelta
}));

vi.mock('$lib/db/entity-info', () => ({
  fetchEntityNames: vi.fn().mockResolvedValue(new Set<string>())
}));

const ONE_HOUR = 3600_000;
const SEVEN_DAYS = 7 * 24 * ONE_HOUR;
const RECENT = Date.now() - ONE_HOUR;
const OLD = Date.now() - SEVEN_DAYS - 1;

describe('syncAll', () => {
  beforeEach(async () => {
    await resetDb();
    vi.stubGlobal('navigator', { onLine: true });
    mockPullFull.mockReset().mockResolvedValue(true);
    mockPullDelta.mockReset().mockResolvedValue(true);
  });

  it('uses delta sync when lastSyncAt is less than 7 days old', async () => {
    await db.meta.put({ key: 'lastSyncAt', value: RECENT });

    const result = await offlineService.syncAll();

    expect(result).toBe(true);
    expect(mockPullDelta).toHaveBeenCalledOnce();
    expect(mockPullFull).not.toHaveBeenCalled();
  });

  it('falls back to full sync when lastSyncAt is older than 7 days', async () => {
    await db.meta.put({ key: 'lastSyncAt', value: OLD });

    const result = await offlineService.syncAll();

    expect(result).toBe(true);
    expect(mockPullDelta).not.toHaveBeenCalled();
    expect(mockPullFull).toHaveBeenCalledOnce();
  });

  it('uses full sync when no lastSyncAt exists', async () => {
    const result = await offlineService.syncAll();

    expect(result).toBe(true);
    expect(mockPullDelta).not.toHaveBeenCalled();
    expect(mockPullFull).toHaveBeenCalledOnce();
  });

  it('returns false when offline', async () => {
    vi.stubGlobal('navigator', { onLine: false });

    const result = await offlineService.syncAll();

    expect(result).toBe(false);
  });

  it('falls back to full sync when delta fails', async () => {
    mockPullDelta.mockResolvedValue(false);
    await db.meta.put({ key: 'lastSyncAt', value: RECENT });

    const result = await offlineService.syncAll();

    expect(result).toBe(true);
    expect(mockPullDelta).toHaveBeenCalledOnce();
    expect(mockPullFull).toHaveBeenCalledOnce();
  });

  it('propagates unauthorized from delta', async () => {
    mockPullDelta.mockResolvedValue('unauthorized');
    await db.meta.put({ key: 'lastSyncAt', value: RECENT });

    const result = await offlineService.syncAll();

    expect(result).toBe('unauthorized');
    expect(mockPullFull).not.toHaveBeenCalled();
  });
});
