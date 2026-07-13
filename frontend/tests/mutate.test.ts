import { describe, it, expect, beforeEach, vi } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { createFetchMock } from './helpers/fetch';
import { mutate } from '$lib/db/mutate';

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

const optimisticUpdate = {
  id: -1,
  data_type: 'weight',
  value_numeric: 75,
  updated_at: '2026-07-13T12:00:00Z'
};

describe('mutate', () => {
  beforeEach(async () => {
    await resetDb();
    vi.clearAllMocks();
    vi.stubGlobal('navigator', { onLine: true });
    localStorage.setItem('salus_token', 'test-token');
  });

  describe('online', () => {
    it('saves server record on create success', async () => {
      const fetchMock = createFetchMock([
        {
          body: {
            results: [
              {
                status: 'created',
                client_id: 'any',
                record: { id: 1, data_type: 'weight', value_numeric: 75 }
              }
            ]
          }
        }
      ]);
      vi.stubGlobal('fetch', fetchMock);

      const result = await mutate({
        table: 'measurement',
        type: 'create',
        optimistic: optimisticUpdate,
        data: { data_type: 'weight', value_numeric: 75 }
      });

      expect(result).toEqual({ ok: true });
      // Temp record (id=-1) removed, server record stored
      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].id).toBe(1);
      expect(mockSyncEngine.enqueue).not.toHaveBeenCalled();
    });

    it('sends expected_updated_at on update', async () => {
      const fetchMock = vi.fn(async (_url: string, init?: RequestInit) => {
        const body = JSON.parse((init?.body as string) ?? '{}');
        expect(body.operations[0].expected_updated_at).toBe('2026-07-13T12:00:00Z');
        return {
          ok: true,
          status: 200,
          json: async () => ({
            results: [{ status: 'updated', client_id: 'any', record: { id: 1 } }]
          }),
          text: async () => '',
          headers: new Headers()
        } as Response;
      });
      vi.stubGlobal('fetch', fetchMock);

      await mutate({
        table: 'measurement',
        type: 'update',
        optimistic: optimisticUpdate,
        data: { value_numeric: 80 },
        realId: 1
      });

      expect(fetchMock).toHaveBeenCalledOnce();
    });

    it('enqueues conflict on conflict response', async () => {
      const fetchMock = createFetchMock([
        {
          body: {
            results: [
              {
                status: 'conflict',
                client_id: 'any',
                conflict: { id: 1, value_numeric: 100, updated_at: '2026-07-13T13:00:00Z' }
              }
            ]
          }
        }
      ]);
      vi.stubGlobal('fetch', fetchMock);

      const result = await mutate({
        table: 'measurement',
        type: 'update',
        optimistic: optimisticUpdate,
        data: { value_numeric: 80 },
        realId: 1
      });

      expect(result).toEqual({ ok: false, conflict: true, error: expect.any(String) });
      expect(mockConflictStore.enqueue).toHaveBeenCalledOnce();
    });

    it('returns error on server error', async () => {
      const fetchMock = createFetchMock([{ status: 422, body: { detail: 'Invalid' } }]);
      vi.stubGlobal('fetch', fetchMock);

      const result = await mutate({
        table: 'measurement',
        type: 'create',
        optimistic: optimisticUpdate
      });

      expect(result.ok).toBe(false);
      expect(result.error).toBeDefined();
    });

    it('falls back to queue on network error', async () => {
      vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network failure')));

      const result = await mutate({
        table: 'measurement',
        type: 'create',
        optimistic: optimisticUpdate,
        data: { data_type: 'weight', value_numeric: 75 }
      });

      expect(result).toEqual({ ok: true });
      expect(mockSyncEngine.enqueue).toHaveBeenCalledOnce();
      expect(mockSyncEngine.enqueue).toHaveBeenCalledWith(
        'create',
        'measurement',
        expect.any(String),
        { data_type: 'weight', value_numeric: 75 },
        undefined,
        undefined
      );
      // optimistic record saved locally
      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].data_type).toBe('weight');
    });
  });

  describe('offline', () => {
    it('saves locally and enqueues', async () => {
      vi.stubGlobal('navigator', { onLine: false });

      const result = await mutate({
        table: 'measurement',
        type: 'create',
        optimistic: optimisticUpdate,
        data: { data_type: 'weight', value_numeric: 75 }
      });

      expect(result).toEqual({ ok: true });
      expect(mockSyncEngine.enqueue).toHaveBeenCalledOnce();
      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].id).toBe(-1);
    });
  });
});
