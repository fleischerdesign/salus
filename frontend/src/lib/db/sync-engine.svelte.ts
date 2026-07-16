import { db } from './database';
import type { OutboxOp, SyncStatus } from './types';
import { getAuthHeaders } from '$lib/api/headers';
import type { Mutation } from '$lib/mutate';

let _status = $state<SyncStatus>('idle');
let _queueLength = $state(0);
let _error = $state<string | null>(null);
let _sessionExpired = $state(false);

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
  get sessionExpired() {
    return _sessionExpired;
  },

  async enqueueOutbox(m: Mutation, clientId: string): Promise<void> {
    const createdAt = new Date().toISOString();
    let op: OutboxOp;

    if (m.kind === 'crud') {
      op = {
        kind: 'crud',
        opType: m.op,
        entity: m.entity,
        client_id: clientId,
        data: m.data,
        realId: m.id,
        expected_updated_at: m.expected_updated_at,
        createdAt,
        retries: 0
      };
    } else {
      op = {
        kind: 'command',
        command: m.command,
        client_id: clientId,
        payload: m.payload,
        optimisticTable: m.optimisticTable,
        optimisticData: m.optimisticData,
        responseTable: m.responseTable,
        createdAt,
        retries: 0
      };
    }

    await db.outbox.put(op);
    _queueLength = await db.outbox.count();
  },

  async flush(): Promise<void> {
    _status = 'syncing';
    _error = null;

    const items = await db.outbox.orderBy('createdAt').toArray();
    if (items.length === 0) {
      _status = 'idle';
      return;
    }

    const headers: Record<string, string> = {
      ...getAuthHeaders(),
      'Content-Type': 'application/json'
    };

    try {
      const batches = _partitionBatches(items);

      for (const batch of batches) {
        await this._sendBatch(batch, headers);
      }
    } catch (e) {
      _status = 'error';
      _error = `Sync push network error: ${String(e)}`;
    }

    _queueLength = await db.outbox.count();
    if (_status === 'syncing') _status = 'idle';
  },

  async _sendBatch(batch: OutboxOp[], headers: Record<string, string>): Promise<void> {
    const MAX_RETRIES = 5;

    const operations = batch.map((op) => {
      if (op.kind === 'crud') {
        return {
          type: op.opType,
          entity: op.entity,
          client_id: op.client_id,
          ...(op.realId ? { id: op.realId } : {}),
          ...(op.data ? { data: op.data } : {}),
          ...(op.expected_updated_at ? { expected_updated_at: op.expected_updated_at } : {})
        };
      } else {
        return {
          type: 'command',
          command: op.command,
          client_id: op.client_id,
          ...(op.payload ? { payload: op.payload } : {})
        };
      }
    });

    const res = await fetch('/api/v1/sync/push', {
      method: 'POST',
      headers,
      body: JSON.stringify({ operations })
    });

    if (!res.ok) {
      if (res.status === 401) {
        _sessionExpired = true;
        _status = 'idle';
        return;
      }
      _status = 'error';
      _error = `Sync push failed: ${res.status}`;
      return;
    }

    const response = await res.json();
    const results = response.results as Array<{
      client_id?: string;
      entity?: string;
      id?: string;
      status: string;
      record?: Record<string, unknown>;
      conflict?: Record<string, unknown>;
      message?: string;
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
        if (r.conflict && r.entity) {
          await db.table(r.entity).put(r.conflict);
        }
        if (r.client_id) succeeded.add(r.client_id);
      }
    }

    for (const item of batch) {
      if (item.id != null && succeeded.has(item.client_id)) {
        await db.outbox.delete(item.id);
      } else if (item.id != null) {
        item.retries = (item.retries ?? 0) + 1;
        if (item.retries >= MAX_RETRIES) {
          await db.outbox.delete(item.id);
          _error = `Op ${item.client_id} exceeded max retries`;
        } else {
          await db.outbox.put(item);
        }
      }
    }
  },

  async flushSingle(
    clientId: string
  ): Promise<{ ok: boolean; error?: string; conflict?: boolean; queued?: boolean }> {
    _status = 'syncing';
    _error = null;

    const items = await db.outbox.orderBy('createdAt').toArray();
    if (items.length === 0) {
      _status = 'idle';
      return { ok: true };
    }

    const headers: Record<string, string> = {
      ...getAuthHeaders(),
      'Content-Type': 'application/json'
    };

    try {
      const operations = items.map((op) => {
        if (op.kind === 'crud') {
          return {
            type: op.opType,
            entity: op.entity,
            client_id: op.client_id,
            ...(op.realId ? { id: op.realId } : {}),
            ...(op.data ? { data: op.data } : {}),
            ...(op.expected_updated_at ? { expected_updated_at: op.expected_updated_at } : {})
          };
        } else {
          return {
            type: 'command',
            command: op.command,
            client_id: op.client_id,
            ...(op.payload ? { payload: op.payload } : {})
          };
        }
      });

      const res = await fetch('/api/v1/sync/push', {
        method: 'POST',
        headers,
        body: JSON.stringify({ operations })
      });

      if (!res.ok) {
        if (res.status === 401) {
          _sessionExpired = true;
          _status = 'idle';
          return { ok: false, error: 'Unauthorized' };
        }
        _status = 'error';
        _error = `Sync push failed: ${res.status}`;
        return { ok: false, error: `Server returned ${res.status}` };
      }

      const response = await res.json();
      const results = response.results as Array<{
        client_id?: string;
        entity?: string;
        id?: string;
        status: string;
        record?: Record<string, unknown>;
        conflict?: Record<string, unknown>;
        message?: string;
      }>;

      const succeeded = new Set<string>();
      let hasConflict = false;
      let errorMsg: string | undefined;

      for (const r of results) {
        if (r.status === 'created' || r.status === 'updated') {
          if (r.record && r.entity) {
            await db.table(r.entity).put(r.record);
          }
          if (r.client_id) succeeded.add(r.client_id);
        }
        if (r.status === 'deleted' && r.client_id) {
          if (r.client_id) succeeded.add(r.client_id);
        }
        if (r.status === 'conflict') {
          hasConflict = true;
          if (r.conflict && r.entity) {
            await db.table(r.entity).put(r.conflict);
          }
          if (r.client_id) succeeded.add(r.client_id);
        }
        if (r.status === 'error') {
          errorMsg = r.message;
        }
      }

      for (const item of items) {
        if (item.id != null && succeeded.has(item.client_id)) {
          await db.outbox.delete(item.id);
        }
      }

      _queueLength = await db.outbox.count();
      _status = 'idle';

      if (hasConflict) {
        return { ok: false, conflict: true, error: 'Conflict detected' };
      }
      if (errorMsg) {
        return { ok: false, error: errorMsg };
      }
      return { ok: true };
    } catch {
      _status = 'error';
      _error = 'Sync push network error';
      return { ok: false, error: 'Network error' };
    }
  },

  async retryFailed(): Promise<void> {
    _error = null;
    _sessionExpired = false;
    await this.flush();
  },

  resetSessionExpired(): void {
    _sessionExpired = false;
  }
};

function _partitionBatches(items: OutboxOp[]): OutboxOp[][] {
  const batches: OutboxOp[][] = [];
  let crudBuffer: OutboxOp[] = [];

  for (const item of items) {
    if (item.kind === 'crud') {
      crudBuffer.push(item);
    } else {
      if (crudBuffer.length > 0) {
        batches.push(crudBuffer);
        crudBuffer = [];
      }
      batches.push([item]);
    }
  }

  if (crudBuffer.length > 0) {
    batches.push(crudBuffer);
  }

  return batches;
}
