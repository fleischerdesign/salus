import { describe, it, expect, beforeEach, vi } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { createFetchMock } from './helpers/fetch';
import { syncEngine } from '$lib/db/sync-engine.svelte';

describe('syncEngine', () => {
  beforeEach(async () => {
    await resetDb();
    await db.queue.clear();
    await db.domainQueue.clear();
    syncEngine.retryFailed();
    vi.stubGlobal('fetch', vi.fn());
  });

  describe('enqueue', () => {
    it('adds an item to the queue and updates queueLength', async () => {
      await syncEngine.enqueue('create', 'measurement', 'client-1', {
        data_type: 'weight'
      });

      const items = await db.queue.toArray();
      expect(items).toHaveLength(1);
      expect(items[0].type).toBe('create');
      expect(items[0].entity).toBe('measurement');
      expect(items[0].client_id).toBe('client-1');
      expect(syncEngine.queueLength).toBe(1);
    });

    it('supports update with expected_updated_at', async () => {
      const updatedAt = '2026-07-13T12:00:00Z';
      await syncEngine.enqueue('update', 'goal', 'client-2', { target_value: 50 }, 1, updatedAt);

      const items = await db.queue.toArray();
      expect(items).toHaveLength(1);
      expect(items[0].realId).toBe(1);
      expect(items[0].expected_updated_at).toBe(updatedAt);
    });
  });

  describe('enqueueDomain', () => {
    it('adds an item to domainQueue and updates queueLength', async () => {
      await syncEngine.enqueueDomain('/api/v1/workouts', 'POST', { name: 'Test' }, 'workout_plan');

      const items = await db.domainQueue.toArray();
      expect(items).toHaveLength(1);
      expect(items[0].url).toBe('/api/v1/workouts');
      expect(items[0].method).toBe('POST');
      expect(syncEngine.queueLength).toBe(1);
    });
  });

  describe('flush', () => {
    it('sends queued operations and removes succeeded items', async () => {
      await syncEngine.enqueue('create', 'measurement', 'client-a', { data_type: 'weight' });

      const fetchMock = createFetchMock([
        {
          body: {
            results: [
              {
                client_id: 'client-a',
                entity: 'measurement',
                status: 'created',
                record: { id: 1, data_type: 'weight' }
              }
            ]
          }
        }
      ]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      const queueItems = await db.queue.toArray();
      expect(queueItems).toHaveLength(0);

      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].id).toBe(1);

      expect(syncEngine.status).toBe('idle');
    });

    it('handles conflicts by saving server records', async () => {
      await syncEngine.enqueue('update', 'measurement', 'client-b', { data_type: 'weight' }, 1);

      const fetchMock = createFetchMock([
        {
          body: {
            results: [
              {
                client_id: 'client-b',
                entity: 'measurement',
                status: 'conflict',
                conflict: { id: 1, data_type: 'weight', value_numeric: 100 }
              }
            ]
          }
        }
      ]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      const queueItems = await db.queue.toArray();
      expect(queueItems).toHaveLength(0);

      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].value_numeric).toBe(100);
    });

    it('sets sessionExpired on 401', async () => {
      await syncEngine.enqueue('create', 'measurement', 'client-c', {});

      const fetchMock = createFetchMock([{ status: 401 }]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      expect(syncEngine.sessionExpired).toBe(true);
      expect(syncEngine.status).toBe('idle');
      const items = await db.queue.toArray();
      expect(items).toHaveLength(1); // kept in queue
    });

    it('sets error on server error', async () => {
      await syncEngine.enqueue('create', 'measurement', 'client-d', {});

      const fetchMock = createFetchMock([{ status: 500 }]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      expect(syncEngine.status).toBe('error');
      expect(syncEngine.error).toContain('500');
      const items = await db.queue.toArray();
      expect(items).toHaveLength(1); // kept in queue
    });

    it('increments retries on individual operation failure', async () => {
      await db.queue.put({
        type: 'create',
        entity: 'measurement',
        client_id: 'client-e',
        data: { data_type: 'weight' },
        createdAt: Date.now(),
        retries: 0
      });

      const fetchMock = createFetchMock([{ body: { results: [] } }]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      const items = await db.queue.toArray();
      expect(items).toHaveLength(1);
      expect(items[0].retries).toBe(1);
      expect(syncEngine.status).toBe('idle');
    });

    it('deletes item after exceeding max retries', async () => {
      // Starting at 4, after increment → 5 ≥ MAX_RETRIES → deleted
      await db.queue.put({
        type: 'create',
        entity: 'measurement',
        client_id: 'client-f',
        data: { data_type: 'weight' },
        createdAt: Date.now(),
        retries: 4
      });

      const fetchMock = createFetchMock([{ body: { results: [] } }]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      const items = await db.queue.toArray();
      expect(items).toHaveLength(0);
      expect(syncEngine.error).toContain('max retries');
    });

    it('flushes domain queue items', async () => {
      await db.domainQueue.put({
        url: '/api/v1/goals',
        method: 'POST',
        body: { target_value: 100 },
        responseTable: 'goal',
        createdAt: new Date().toISOString()
      });

      const fetchMock = createFetchMock([{ body: { id: 1, target_value: 100 } }]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      const items = await db.domainQueue.toArray();
      expect(items).toHaveLength(0);

      const goals = await db.goal.toArray();
      expect(goals).toHaveLength(1);
      expect(goals[0].target_value).toBe(100);
    });

    it('is a no-op when both queues are empty', async () => {
      await syncEngine.flush();
      expect(syncEngine.status).toBe('idle');
    });
  });
});
