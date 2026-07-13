import { describe, it, expect, beforeEach, vi } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { createFetchMock } from './helpers/fetch';
import { mutateDomain } from '$lib/db/mutate-domain';

const { mockSyncEngine, mockConflictStore } = vi.hoisted(() => ({
  mockSyncEngine: {
    enqueue: vi.fn().mockResolvedValue(undefined),
    enqueueDomain: vi.fn().mockResolvedValue(undefined),
    flush: vi.fn().mockResolvedValue(undefined),
    retryFailed: vi.fn().mockResolvedValue(undefined),
    resetSessionExpired: vi.fn(),
    status: 'idle' as string,
    queueLength: 0 as number,
    error: null as string | null,
    sessionExpired: false as boolean
  },
  mockConflictStore: {
    enqueue: vi.fn(),
    resolve: vi.fn(),
    current: null,
    hasPending: false
  }
}));

vi.mock('$lib/db/sync-engine.svelte', () => ({
  syncEngine: mockSyncEngine
}));

vi.mock('$stores/conflict.svelte', () => ({
  conflictStore: mockConflictStore
}));

describe('mutateDomain', () => {
  beforeEach(async () => {
    await resetDb();
    vi.clearAllMocks();
    vi.stubGlobal('navigator', { onLine: true });
    localStorage.setItem('salus_token', 'test-token');
  });

  describe('online', () => {
    it('stores response record and removes temp id on success', async () => {
      const fetchMock = createFetchMock([{ body: { id: 1, target_value: 100 } }]);
      vi.stubGlobal('fetch', fetchMock);

      const result = await mutateDomain({
        url: '/api/v1/goals',
        method: 'POST',
        body: { target_value: 100 },
        optimisticTable: 'goal',
        optimisticData: { id: -1, target_value: 100 },
        optimisticId: -1,
        responseTable: 'goal'
      });

      expect(result).toEqual({ ok: true, queued: false, data: { id: 1, target_value: 100 } });
      const goals = await db.goal.toArray();
      expect(goals).toHaveLength(1);
      expect(goals[0].id).toBe(1);
    });

    it('handles 204 with optimistic delete', async () => {
      const fetchMock = createFetchMock([{ status: 204 }]);
      vi.stubGlobal('fetch', fetchMock);
      await db.table('goal').put({
        id: 5,
        target_value: 100,
        user_id: 1,
        metric_type_id: 1,
        direction: 'up',
        frequency: 'daily',
        is_active: true,
        deadline: null,
        created_at: '',
        updated_at: null,
        deleted_at: null
      });

      const result = await mutateDomain({
        url: '/api/v1/goals/5',
        method: 'DELETE',
        optimisticTable: 'goal',
        optimisticId: 5
      });

      expect(result).toEqual({ ok: true, queued: false });
      const goals = await db.goal.toArray();
      expect(goals).toHaveLength(0);
    });

    it('enqueues conflict on 409', async () => {
      const fetchMock = createFetchMock([{ status: 409, body: { id: 1, target_value: 200 } }]);
      vi.stubGlobal('fetch', fetchMock);

      const result = await mutateDomain({
        url: '/api/v1/goals',
        method: 'POST',
        body: { target_value: 100 },
        optimisticTable: 'goal',
        optimisticData: { id: -1, target_value: 100 },
        responseTable: 'goal'
      });

      expect(result.ok).toBe(false);
      expect(result.queued).toBe(false);
      expect(result.error).toBe('Conflict');
      expect(mockConflictStore.enqueue).toHaveBeenCalledOnce();
    });

    it('returns unauthorized on 401', async () => {
      const fetchMock = createFetchMock([{ status: 401 }]);
      vi.stubGlobal('fetch', fetchMock);

      const result = await mutateDomain({
        url: '/api/v1/goals',
        method: 'POST'
      });

      expect(result).toEqual({ ok: false, queued: false, error: 'Unauthorized' });
    });

    it('falls back to queue on network error', async () => {
      vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network failure')));

      const result = await mutateDomain({
        url: '/api/v1/goals',
        method: 'POST',
        body: { target_value: 100 },
        optimisticTable: 'goal',
        optimisticData: { id: -1, target_value: 100 },
        optimisticId: -1,
        responseTable: 'goal'
      });

      expect(result).toEqual({ ok: true, queued: true });
      expect(mockSyncEngine.enqueueDomain).toHaveBeenCalledOnce();
      expect(mockSyncEngine.enqueueDomain).toHaveBeenCalledWith(
        '/api/v1/goals',
        'POST',
        { target_value: 100 },
        'goal'
      );
      const goals = await db.goal.toArray();
      expect(goals).toHaveLength(1);
    });
  });

  describe('offline', () => {
    it('saves locally and enqueues', async () => {
      vi.stubGlobal('navigator', { onLine: false });

      const result = await mutateDomain({
        url: '/api/v1/goals',
        method: 'POST',
        body: { target_value: 100 },
        optimisticTable: 'goal',
        optimisticData: { id: -1, target_value: 100 },
        optimisticId: -1,
        responseTable: 'goal'
      });

      expect(result).toEqual({ ok: true, queued: true });
      expect(mockSyncEngine.enqueueDomain).toHaveBeenCalledOnce();
      const goals = await db.goal.toArray();
      expect(goals).toHaveLength(1);
    });
  });
});
