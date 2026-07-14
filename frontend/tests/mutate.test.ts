import { describe, it, expect, beforeEach, vi } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { createFetchMock } from './helpers/fetch';
import { mutate } from '$lib/mutate';

const { mockSyncEngine, mockConflictStore } = vi.hoisted(() => ({
  mockSyncEngine: {
    enqueueOutbox: vi.fn().mockResolvedValue(undefined),
    flushSingle: vi.fn().mockResolvedValue({ ok: true }),
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
  id: 'uid-test-1',
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
      mockSyncEngine.flushSingle.mockResolvedValueOnce({ ok: true });
      await db.outbox.clear();

      const result = await mutate({
        kind: 'crud',
        op: 'create',
        entity: 'measurement',
        optimistic: optimisticUpdate,
        data: { data_type: 'weight', value_numeric: 75 }
      });

      expect(result.ok).toBe(true);
      expect(mockSyncEngine.enqueueOutbox).toHaveBeenCalledOnce();
    });

    it('enqueues conflict on conflict response', async () => {
      mockSyncEngine.flushSingle.mockResolvedValueOnce({ ok: false, conflict: true, error: 'Conflict' });

      const result = await mutate({
        kind: 'crud',
        op: 'update',
        entity: 'measurement',
        optimistic: optimisticUpdate,
        data: { value_numeric: 80 },
        id: 'uid-1'
      });

      expect(result.ok).toBe(false);
      expect(result.conflict).toBe(true);
    });

    it('falls back to queue on network error', async () => {
      vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Network failure')));

      const result = await mutate({
        kind: 'crud',
        op: 'create',
        entity: 'measurement',
        optimistic: optimisticUpdate,
        data: { data_type: 'weight', value_numeric: 75 }
      });

      expect(result.ok).toBe(true);
      expect(mockSyncEngine.enqueueOutbox).toHaveBeenCalledOnce();
      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].data_type).toBe('weight');
    });
  });

  describe('offline', () => {
    it('saves locally and enqueues', async () => {
      vi.stubGlobal('navigator', { onLine: false });

      const result = await mutate({
        kind: 'crud',
        op: 'create',
        entity: 'measurement',
        optimistic: optimisticUpdate,
        data: { data_type: 'weight', value_numeric: 75 }
      });

      expect(result).toEqual({ ok: true, queued: true });
      expect(mockSyncEngine.enqueueOutbox).toHaveBeenCalledOnce();
      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].id).toBe('uid-test-1');
    });
  });
});