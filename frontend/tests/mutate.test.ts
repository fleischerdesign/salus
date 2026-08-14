import { describe, it, expect, beforeEach, vi } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { createFetchMock } from './helpers/fetch';
import { mutate } from '$lib/mutate';
import { localMode } from '$lib/db/local-mode.svelte';

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
  source_data_type: 'weight',
  value_numeric: 75,
  updated_at: '2026-07-13T12:00:00Z'
};

describe('mutate', () => {
  beforeEach(async () => {
    await resetDb();
    vi.clearAllMocks();
    vi.stubGlobal('navigator', { onLine: true });
    localStorage.setItem('salus_token', 'test-token');
    localMode.disable();
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
        data: { source_data_type: 'weight', value_numeric: 75 }
      });

      expect(result.ok).toBe(true);
      expect(mockSyncEngine.enqueueOutbox).toHaveBeenCalledOnce();
    });

    it('merges partial optimistic updates into the existing row', async () => {
      mockSyncEngine.flushSingle.mockResolvedValueOnce({ ok: true });
      await db.outbox.clear();
      await db.measurement.put({
        id: 'uid-test-1',
        user_id: 'u',
        metric_code: 'weight',
        source_data_type: 'weight',
        source: 'manual',
        value_numeric: 70,
        value_text: null,
        value_json: null,
        start_time: '2026-08-14T08:00:00Z',
        end_time: null,
        notes: null,
        external_id: null,
        created_at: new Date().toISOString(),
        updated_at: null,
        deleted_at: null
      });

      const result = await mutate({
        kind: 'crud',
        op: 'update',
        entity: 'measurement',
        id: 'uid-test-1',
        optimistic: { id: 'uid-test-1', value_numeric: 75 },
        data: { value_numeric: 75 }
      });

      expect(result.ok).toBe(true);
      const row = await db.measurement.get('uid-test-1');
      expect(row?.value_numeric).toBe(75);
      expect(row?.source_data_type).toBe('weight');
      expect(row?.start_time).toBe('2026-08-14T08:00:00Z');
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
        data: { source_data_type: 'weight', value_numeric: 75 }
      });

      expect(result.ok).toBe(true);
      expect(mockSyncEngine.enqueueOutbox).toHaveBeenCalledOnce();
      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].source_data_type).toBe('weight');
    });

    it('extracts expected_updated_at from the local record on update', async () => {
      await db.measurement.put({
        id: 'uid-1',
        user_id: 'self',
        metric_code: 'weight',
        source_data_type: 'weight',
        source: 'manual',
        value_numeric: 75,
        value_text: null,
        value_json: null,
        start_time: '2026-07-13T12:00:00Z',
        end_time: null,
        notes: null,
        external_id: null,
        created_at: '2026-07-13T12:00:00Z',
        updated_at: '2026-07-13T12:00:00Z',
        deleted_at: null
      });

      await mutate({
        kind: 'crud',
        op: 'update',
        entity: 'measurement',
        id: 'uid-1',
        optimistic: { id: 'uid-1', value_numeric: 80 },
        data: { value_numeric: 80 }
      });

      const enqueued = mockSyncEngine.enqueueOutbox.mock.calls[0][0];
      expect(enqueued.expected_updated_at).toBe('2026-07-13T12:00:00Z');
    });

    it('does not set expected_updated_at when the record has none', async () => {
      await db.measurement.put({
        id: 'uid-2',
        user_id: 'self',
        metric_code: 'weight',
        source_data_type: 'weight',
        source: 'manual',
        value_numeric: 75,
        value_text: null,
        value_json: null,
        start_time: '2026-07-13T12:00:00Z',
        end_time: null,
        notes: null,
        external_id: null,
        created_at: '2026-07-13T12:00:00Z',
        updated_at: null,
        deleted_at: null
      });

      await mutate({
        kind: 'crud',
        op: 'update',
        entity: 'measurement',
        id: 'uid-2',
        optimistic: { id: 'uid-2', value_numeric: 80 },
        data: { value_numeric: 80 }
      });

      const enqueued = mockSyncEngine.enqueueOutbox.mock.calls[0][0];
      expect(enqueued.expected_updated_at).toBeUndefined();
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
        data: { source_data_type: 'weight', value_numeric: 75 }
      });

      expect(result).toEqual({ ok: true, queued: true });
      expect(mockSyncEngine.enqueueOutbox).toHaveBeenCalledOnce();
      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].id).toBe('uid-test-1');
    });

    it('queues without flushing in local mode', async () => {
      localMode.enable();

      const result = await mutate({
        kind: 'crud',
        op: 'create',
        entity: 'measurement',
        optimistic: optimisticUpdate,
        data: { source_data_type: 'weight', value_numeric: 75 }
      });

      expect(result).toEqual({ ok: true, queued: true });
      expect(mockSyncEngine.enqueueOutbox).toHaveBeenCalledOnce();
      expect(mockSyncEngine.flushSingle).not.toHaveBeenCalled();
    });
  });
});