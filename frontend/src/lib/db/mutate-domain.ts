import { db } from './database';
import { syncEngine } from './sync-engine.svelte';
import { getAuthHeaders } from '$lib/api/headers';
import { conflictStore } from '$stores/conflict.svelte';

function isOnline(): boolean {
  return typeof navigator !== 'undefined' ? navigator.onLine : true;
}

interface DomainMutateOpts {
  url: string;
  method?: 'POST' | 'PUT' | 'DELETE';
  body?: Record<string, unknown>;
  optimisticTable?: string;
  optimisticData?: Record<string, unknown>;
  optimisticId?: number;
  responseTable?: string;
}

export async function mutateDomain(
  opts: DomainMutateOpts
): Promise<{ ok: boolean; data?: unknown; queued: boolean; error?: string; conflict?: unknown }> {
  const {
    url,
    method = 'POST',
    body,
    optimisticTable,
    optimisticData,
    optimisticId,
    responseTable
  } = opts;

  if (isOnline()) {
    try {
      const headers: Record<string, string> = {
        ...getAuthHeaders(),
        'Content-Type': 'application/json'
      };

      const res = await fetch(url, {
        method,
        headers: method !== 'DELETE' ? headers : { ...headers, 'Content-Type': '' },
        body: body && method !== 'DELETE' ? JSON.stringify(body) : undefined
      });

      if (res.status === 409) {
        const conflictData = await res.json().catch(() => null);
        if (conflictData && responseTable && optimisticData) {
          conflictStore.enqueue({
            id: crypto.randomUUID(),
            table: responseTable,
            clientRecord: optimisticData,
            serverRecord: conflictData as Record<string, unknown>,
            retryData: body
          });
        }
        return { ok: false, queued: false, error: 'Conflict', conflict: conflictData };
      }

      if (res.status === 401) {
        return { ok: false, queued: false, error: 'Unauthorized' };
      }

      if (!res.ok) {
        return { ok: false, queued: false, error: `Server returned ${res.status}` };
      }

      if (responseTable && res.status !== 204) {
        const data = await res.json();
        const merged = optimisticData ? { ...optimisticData, ...data } : data;
        await db.table(responseTable).put(merged);
        if (optimisticId != null && optimisticId < 0 && optimisticTable) {
          await db.table(optimisticTable || responseTable).delete(optimisticId);
        }
        return { ok: true, data, queued: false };
      }

      if (optimisticTable && optimisticId != null && (method === 'DELETE' || optimisticId < 0)) {
        await db.table(optimisticTable).delete(optimisticId);
      }

      return { ok: true, queued: false };
    } catch {
      if (method === 'DELETE' && optimisticId != null && optimisticTable) {
        await db.table(optimisticTable).delete(optimisticId);
      } else if (optimisticTable && optimisticData) {
        await db.table(optimisticTable).put(optimisticData);
      }
      await syncEngine.enqueueDomain(url, method, body, responseTable);
      return { ok: true, queued: true };
    }
  }

  if (method === 'DELETE' && optimisticId != null && optimisticTable) {
    await db.table(optimisticTable).delete(optimisticId);
  } else if (optimisticTable && optimisticData) {
    await db.table(optimisticTable).put(optimisticData);
  }
  await syncEngine.enqueueDomain(url, method, body, responseTable);
  return { ok: true, queued: true };
}
