import { describe, it, expect, beforeEach, vi } from 'vitest';
import { db } from '$lib/db/database';
import { resetDb } from './helpers/db';
import { createFetchMock } from './helpers/fetch';
import { syncEngine } from '$lib/db/sync-engine.svelte';
import type { OutboxCrudOp } from '$lib/db/types';

describe('syncEngine', () => {
  beforeEach(async () => {
    await resetDb();
    await db.outbox.clear();
    syncEngine.retryFailed();
    vi.stubGlobal('fetch', vi.fn());
  });

  describe('enqueueOutbox', () => {
    it('adds a crud item to the outbox and updates queueLength', async () => {
      await syncEngine.enqueueOutbox(
        { kind: 'crud', op: 'create', entity: 'measurement', data: { data_type: 'weight' } },
        'client-1'
      );

      const items = await db.outbox.toArray();
      expect(items).toHaveLength(1);
      const crudItem = items[0];
      expect(crudItem.kind).toBe('crud');
      if (crudItem.kind === 'crud') {
        expect(crudItem.opType).toBe('create');
        expect(crudItem.entity).toBe('measurement');
        expect(crudItem.client_id).toBe('client-1');
      }
      expect(syncEngine.queueLength).toBe(1);
    });

    it('supports update with expected_updated_at', async () => {
      const updatedAt = '2026-07-13T12:00:00Z';
      await syncEngine.enqueueOutbox(
        { kind: 'crud', op: 'update', entity: 'goal', data: { target_value: 50 }, id: '1', expected_updated_at: updatedAt },
        'client-2'
      );

      const items = await db.outbox.toArray();
      expect(items).toHaveLength(1);
      const item = items[0];
      if (item.kind === 'crud') {
        expect(item.realId).toBe('1');
        expect(item.expected_updated_at).toBe(updatedAt);
      }
    });
  });

  describe('flush', () => {
    it('sends queued operations and removes succeeded items', async () => {
      await syncEngine.enqueueOutbox(
        { kind: 'crud', op: 'create', entity: 'measurement', data: { data_type: 'weight' } },
        'client-a'
      );

      const fetchMock = createFetchMock([
        {
          body: {
            results: [
              {
                client_id: 'client-a',
                entity: 'measurement',
                status: 'created',
                record: { id: 'uid-1', data_type: 'weight' }
              }
            ]
          }
        }
      ]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      const outboxItems = await db.outbox.toArray();
      expect(outboxItems).toHaveLength(0);

      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].id).toBe('uid-1');

      expect(syncEngine.status).toBe('idle');
    });

    it('handles conflicts by saving server records', async () => {
      await syncEngine.enqueueOutbox(
        { kind: 'crud', op: 'update', entity: 'measurement', data: { data_type: 'weight' }, id: '1' },
        'client-b'
      );

      const fetchMock = createFetchMock([
        {
          body: {
            results: [
              {
                client_id: 'client-b',
                entity: 'measurement',
                status: 'conflict',
                conflict: { id: 'uid-1', data_type: 'weight', value_numeric: 100 }
              }
            ]
          }
        }
      ]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      const outboxItems = await db.outbox.toArray();
      expect(outboxItems).toHaveLength(0);

      const measurements = await db.measurement.toArray();
      expect(measurements).toHaveLength(1);
      expect(measurements[0].value_numeric).toBe(100);
    });

    it('sets sessionExpired on 401', async () => {
      await syncEngine.enqueueOutbox(
        { kind: 'crud', op: 'create', entity: 'measurement' },
        'client-c'
      );

      const fetchMock = createFetchMock([{ status: 401 }]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      expect(syncEngine.sessionExpired).toBe(true);
      expect(syncEngine.status).toBe('idle');
      const items = await db.outbox.toArray();
      expect(items).toHaveLength(1);
    });

    it('sets error on server error', async () => {
      await syncEngine.enqueueOutbox(
        { kind: 'crud', op: 'create', entity: 'measurement' },
        'client-d'
      );

      const fetchMock = createFetchMock([{ status: 500 }]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      expect(syncEngine.status).toBe('error');
      expect(syncEngine.error).toContain('500');
      const items = await db.outbox.toArray();
      expect(items).toHaveLength(1);
    });

    it('increments retries on individual operation failure', async () => {
      await db.outbox.put({
        kind: 'crud',
        opType: 'create',
        entity: 'measurement',
        client_id: 'client-e',
        data: { data_type: 'weight' },
        createdAt: new Date().toISOString(),
        retries: 0
      } as OutboxCrudOp);

      const fetchMock = createFetchMock([{ body: { results: [] } }]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      const items = await db.outbox.toArray();
      expect(items).toHaveLength(1);
      expect(items[0].retries).toBe(1);
      expect(syncEngine.status).toBe('idle');
    });

    it('deletes item after exceeding max retries', async () => {
      await db.outbox.put({
        kind: 'crud',
        opType: 'create',
        entity: 'measurement',
        client_id: 'client-f',
        data: { data_type: 'weight' },
        createdAt: new Date().toISOString(),
        retries: 4
      } as OutboxCrudOp);

      const fetchMock = createFetchMock([{ body: { results: [] } }]);
      vi.stubGlobal('fetch', fetchMock);

      await syncEngine.flush();

      const items = await db.outbox.toArray();
      expect(items).toHaveLength(0);
      expect(syncEngine.error).toContain('max retries');
    });

    it('is a no-op when outbox is empty', async () => {
      await syncEngine.flush();
      expect(syncEngine.status).toBe('idle');
    });
  });
});