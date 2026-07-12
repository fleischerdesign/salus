import { db } from './database';
import { syncEngine } from './sync-engine.svelte';
import { getAuthHeaders } from '$lib/api/headers';
import { conflictStore } from '$stores/conflict.svelte';

let _tempIdCounter = -1;
export function nextTempId(): number {
  return _tempIdCounter--;
}

function isOnline(): boolean {
  return typeof navigator !== 'undefined' ? navigator.onLine : true;
}

interface MutateOpts {
  table: string;
  type: 'create' | 'update' | 'delete';
  data?: Record<string, unknown>;
  optimistic: Record<string, unknown>;
  realId?: number;
  onSuccess?: () => Promise<void>;
}

export async function mutate(
  opts: MutateOpts
): Promise<{ ok: boolean; error?: string; conflict?: boolean }> {
  const clientId = crypto.randomUUID();

  if (isOnline()) {
    try {
      const headers: Record<string, string> = {
        ...getAuthHeaders(),
        'Content-Type': 'application/json'
      };

      const operation: Record<string, unknown> = {
        type: opts.type,
        entity: opts.table,
        client_id: clientId
      };
      if (opts.data) operation['data'] = opts.data;
      if (opts.realId != null && opts.realId > 0) operation['id'] = opts.realId;

      if (opts.type === 'update' && opts.optimistic.updated_at) {
        operation['expected_updated_at'] = opts.optimistic.updated_at as string;
      }

      const res = await fetch('/api/v1/sync/push', {
        method: 'POST',
        headers,
        body: JSON.stringify({ operations: [operation] })
      });

      if (!res.ok) {
        return { ok: false, error: `Server returned ${res.status}` };
      }

      const response = await res.json();
      const result = response.results?.[0];

      if (result?.status === 'created' || result?.status === 'updated') {
        if (result.record) {
          const tempId = opts.optimistic.id as number;
          if (tempId < 0) await db.table(opts.table).delete(tempId);
          await db.table(opts.table).put(result.record);
        }
        if (opts.onSuccess) await opts.onSuccess();
        return { ok: true };
      }

      if (result?.status === 'deleted') {
        await db.table(opts.table).delete(opts.optimistic.id as number);
        if (opts.onSuccess) await opts.onSuccess();
        return { ok: true };
      }

      if (result?.status === 'conflict') {
        conflictStore.enqueue({
          id: crypto.randomUUID(),
          table: opts.table,
          realId: opts.realId,
          clientRecord: opts.optimistic,
          serverRecord: (result.conflict as Record<string, unknown>) ?? opts.optimistic,
          retryData: opts.data
        });
        return { ok: false, conflict: true, error: 'Conflict detected — review required' };
      }

      return { ok: false, error: result?.message || result?.status || 'Unknown error' };
    } catch (e) {
      await db.table(opts.table).put(opts.optimistic);
      const expectedUpdatedAt =
        opts.type === 'update' && opts.optimistic.updated_at
          ? (opts.optimistic.updated_at as string | undefined)
          : undefined;
      await syncEngine.enqueue(
        opts.type,
        opts.table,
        clientId,
        opts.data,
        opts.realId,
        expectedUpdatedAt
      );
      return { ok: true };
    }
  }

  await db.table(opts.table).put(opts.optimistic);
  const expectedUpdatedAt =
    opts.type === 'update' && opts.optimistic.updated_at
      ? (opts.optimistic.updated_at as string | undefined)
      : undefined;
  await syncEngine.enqueue(
    opts.type,
    opts.table,
    clientId,
    opts.data,
    opts.realId,
    expectedUpdatedAt
  );
  return { ok: true };
}
