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

describe('mutate (command)', () => {
  beforeEach(async () => {
    await resetDb();
    vi.clearAllMocks();
    vi.stubGlobal('navigator', { onLine: true });
    localStorage.setItem('salus_token', 'test-token');
  });

  describe('queueable command', () => {
    it('enqueues to outbox when online', async () => {
      mockSyncEngine.flushSingle.mockResolvedValueOnce({ ok: true });

      const result = await mutate({
        kind: 'command',
        command: 'start_workout',
        queueable: true,
        payload: { plan_id: 'uid-plan' },
        optimisticTable: 'workout_session',
        optimisticData: { id: 'uid-session', plan_id: 'uid-plan' },
        responseTable: 'workout_session'
      });

      expect(result.ok).toBe(true);
      expect(mockSyncEngine.enqueueOutbox).toHaveBeenCalledOnce();
    });

    it('saves locally and enqueues when offline', async () => {
      vi.stubGlobal('navigator', { onLine: false });

      const result = await mutate({
        kind: 'command',
        command: 'start_workout',
        queueable: true,
        payload: { plan_id: 'uid-plan' },
        optimisticTable: 'workout_session',
        optimisticData: { id: 'uid-session', plan_id: 'uid-plan' }
      });

      expect(result).toEqual({ ok: true, queued: true });
      expect(mockSyncEngine.enqueueOutbox).toHaveBeenCalledOnce();
    });
  });

  describe('non-queueable command', () => {
    it('returns error when offline', async () => {
      vi.stubGlobal('navigator', { onLine: false });

      const result = await mutate({
        kind: 'command',
        command: 'change_password',
        queueable: false,
        payload: { current_password: 'old', new_password: 'new' }
      });

      expect(result.ok).toBe(false);
      expect(result.error).toContain('internet');
      expect(mockSyncEngine.enqueueOutbox).not.toHaveBeenCalled();
    });

    it('sends immediately when online', async () => {
      const fetchMock = createFetchMock([
        {
          body: {
            results: [
              { status: 'updated', client_id: 'any' }
            ]
          }
        }
      ]);
      vi.stubGlobal('fetch', fetchMock);

      const result = await mutate({
        kind: 'command',
        command: 'change_password',
        queueable: false,
        payload: { current_password: 'old', new_password: 'new' }
      });

      expect(result.ok).toBe(true);
      expect(mockSyncEngine.enqueueOutbox).not.toHaveBeenCalled();
    });
  });
});