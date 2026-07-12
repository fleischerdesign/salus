import { db } from './database';
import type { QueueOp, SyncStatus } from './types';
import { getAuthHeaders } from '$lib/api/headers';

let _status = $state<SyncStatus>('idle');
let _queueLength = $state(0);
let _error = $state<string | null>(null);

export const syncEngine = {
  get status() {
    return _status;
  },
  get queueLength() {
    return _queueLength;
  },
  get error() {
    return _error;
  },

  async enqueue(
    type: QueueOp['type'],
    entity: string,
    client_id: string,
    data?: Record<string, unknown>,
  ): Promise<void> {
    await db.queue.put({
      type,
      entity,
      client_id,
      data,
      createdAt: Date.now(),
      retries: 0,
    });
    _queueLength = await db.queue.count() + await db.domainQueue.count();
  },

  async enqueueDomain(
    url: string,
    method: string,
    body?: Record<string, unknown>,
    responseTable?: string,
  ): Promise<void> {
    await db.domainQueue.put({
      url,
      method,
      body,
      responseTable,
      createdAt: new Date().toISOString(),
    });
    _queueLength = await db.queue.count() + await db.domainQueue.count();
  },

  async flush(): Promise<void> {
    _status = 'syncing';
    _error = null;

    await this._flushEntityQueue();
    await this._flushDomainQueue();

    _queueLength = await db.queue.count() + await db.domainQueue.count();
    if (_status === 'syncing') _status = 'idle';
  },

  async _flushEntityQueue(): Promise<void> {
    const items = await db.queue.orderBy('createdAt').toArray();
    if (items.length === 0) return;

    const headers: Record<string, string> = { ...getAuthHeaders(), 'Content-Type': 'application/json' };

    try {
      const operations = items.map((op) => ({
        type: op.type,
        entity: op.entity,
        client_id: op.client_id,
        ...(op.data ? { data: op.data } : {}),
      }));

      const res = await fetch('/api/v1/sync/push', {
        method: 'POST',
        headers,
        body: JSON.stringify({ operations }),
      });

      if (!res.ok) {
        _status = 'error';
        _error = `Sync push failed: ${res.status}`;
        return;
      }

      const response = await res.json();
      const results = response.results as Array<{
        client_id?: string;
        entity: string;
        id?: number;
        status: string;
        record?: Record<string, unknown>;
      }>;

      const succeeded = new Set<string>();
      for (const r of results) {
        if (r.status === 'created' || r.status === 'updated') {
          if (r.record && r.entity) {
            await db.table(r.entity).put(r.record);
          }
          if (r.client_id) succeeded.add(r.client_id);
        }
        if (r.status === 'deleted' && r.client_id) {
          succeeded.add(r.client_id);
        }
        if (r.status === 'conflict') {
          if (r.record && r.entity) {
            await db.table(r.entity).put(r.record);
          }
          if (r.client_id) succeeded.add(r.client_id);
        }
      }

      const MAX_RETRIES = 5;
      for (const item of items) {
        if (item.id != null && succeeded.has(item.client_id)) {
          await db.queue.delete(item.id);
        } else if (item.id != null) {
          item.retries = (item.retries ?? 0) + 1;
          if (item.retries >= MAX_RETRIES) {
            await db.queue.delete(item.id);
            _error = `Op ${item.client_id} exceeded max retries`;
          } else {
            await db.queue.put(item);
          }
        }
      }
    } catch (e) {
      _status = 'error';
      _error = `Sync push network error: ${String(e)}`;
    }
  },

  async _flushDomainQueue(): Promise<void> {
    const items = await db.domainQueue.orderBy('createdAt').toArray();
    if (items.length === 0) return;

    const MAX_RETRIES = 5;

    for (const item of items) {
      try {
        const headers: Record<string, string> = { ...getAuthHeaders() };
        if (item.method !== 'DELETE') headers['Content-Type'] = 'application/json';

        const res = await fetch(item.url, {
          method: item.method,
          headers,
          body: item.body && item.method !== 'DELETE' ? JSON.stringify(item.body) : undefined,
        });

        if (res.ok && item.responseTable && res.status !== 204) {
          const data = await res.json();
          await db.table(item.responseTable).put(data);
        }

        if (item.id != null) {
          await db.domainQueue.delete(item.id);
        }
      } catch {
        if (item.id != null) {
          const retries = ((item as unknown as Record<string, unknown>).retries as number ?? 0) + 1;
          if (retries >= MAX_RETRIES) {
            await db.domainQueue.delete(item.id);
            _error = `Domain op exceeded max retries: ${item.url}`;
          } else {
            await db.domainQueue.update(item.id, { retries } as unknown as Record<string, unknown>);
          }
        }
      }
    }
  },

  async retryFailed(): Promise<void> {
    _error = null;
    await this.flush();
  },
};
