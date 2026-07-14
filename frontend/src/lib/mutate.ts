import { db } from './db/database';
import { syncEngine } from './db/sync-engine.svelte';
import { getAuthHeaders } from '$lib/api/headers';
import { uuid7 } from './db/uuid';

function isOnline(): boolean {
  return typeof navigator !== 'undefined' ? navigator.onLine : true;
}

export type Mutation =
  | {
      kind: 'crud';
      op: 'create' | 'update' | 'delete';
      entity: string;
      data?: Record<string, unknown>;
      id?: string;
      optimistic?: Record<string, unknown>;
      expected_updated_at?: string;
    }
  | {
      kind: 'command';
      command: string;
      payload?: Record<string, unknown>;
      queueable: boolean;
      optimisticTable?: string;
      optimisticData?: Record<string, unknown>;
      responseTable?: string;
    };

export interface MutationResult {
  ok: boolean;
  error?: string;
  conflict?: boolean;
  data?: unknown;
  queued?: boolean;
}

export async function mutate(m: Mutation): Promise<MutationResult> {
  const clientId = uuid7();

  if (m.kind === 'command' && !m.queueable) {
    return sendCommandNow(m, clientId);
  }

  await applyOptimistic(m);
  await syncEngine.enqueueOutbox(m, clientId);

  if (isOnline()) {
    const result = await syncEngine.flushSingle(clientId);
    return result;
  }

  return { ok: true, queued: true };
}

async function applyOptimistic(m: Mutation): Promise<void> {
  if (m.kind === 'crud' && m.op === 'delete' && m.id) {
    await db.table(m.entity).delete(m.id);
    return;
  }

  const table = m.kind === 'crud' ? m.entity : m.optimisticTable;
  const data = m.kind === 'crud' ? m.optimistic : m.optimisticData;
  if (table && data) {
    await db.table(table).put(data);
  }
}

async function sendCommandNow(
  m: Mutation & { kind: 'command' },
  clientId: string
): Promise<MutationResult> {
  if (!isOnline()) {
    return { ok: false, error: 'This action requires an internet connection' };
  }

  try {
    const res = await fetch('/api/v1/sync/push', {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        operations: [
          {
            type: 'command',
            command: m.command,
            client_id: clientId,
            payload: m.payload || {}
          }
        ]
      })
    });

    if (res.status === 401) {
      return { ok: false, error: 'Unauthorized' };
    }

    if (!res.ok) {
      return { ok: false, error: `Server returned ${res.status}` };
    }

    const response = await res.json();
    const result = response.results?.[0];

    if (result?.status === 'created' || result?.status === 'updated') {
      if (result.record && m.responseTable) {
        await db.table(m.responseTable).put(result.record);
      }
      return { ok: true, data: result.record };
    }

    if (result?.status === 'deleted') {
      return { ok: true };
    }

    if (result?.status === 'error') {
      return { ok: false, error: result.message || 'Command failed' };
    }

    return { ok: false, error: result?.message || result?.status || 'Unknown error' };
  } catch {
    return { ok: false, error: 'Network error' };
  }
}
