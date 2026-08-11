import { db } from './database';
import { rawGet } from '$lib/api/client';
import { fetchEntityNames } from './entity-info';

const SYNC_META_KEYS = new Set(['cursors', 'has_more', 'synced_at']);
const CHUNK_SIZE = 500;

function isRecordArray(value: unknown): value is Record<string, unknown>[] {
  return Array.isArray(value);
}

function saturatingProgress(batch: number): number {
  return 0.05 + 0.55 * (1 - Math.exp(-batch * 0.4));
}

interface FullSyncResponse {
  cursors: Record<string, number>;
  has_more: boolean;
  synced_at: string;
  [table: string]: unknown;
}

interface DeltaResponse {
  changed: Record<string, Record<string, unknown>[]>;
  deleted: Record<string, (string | number)[]>;
  synced_at: string;
}

/**
 * Persists records into a Dexie table in bounded chunks
 * to guarantee O(1) peak memory consumption and prevent UI thread starvation.
 */
async function _bulkPutChunked(table: string, rows: Record<string, unknown>[]): Promise<void> {
  const tableRef = db.table(table);
  for (let i = 0; i < rows.length; i += CHUNK_SIZE) {
    const chunk = rows.slice(i, i + CHUNK_SIZE);
    await tableRef.bulkPut(chunk);
  }
}

/**
 * Deletes records from a Dexie table in bounded chunks.
 */
async function _bulkDeleteChunked(table: string, ids: (string | number)[]): Promise<void> {
  const tableRef = db.table(table);
  for (let i = 0; i < ids.length; i += CHUNK_SIZE) {
    const chunk = ids.slice(i, i + CHUNK_SIZE);
    await tableRef.bulkDelete(chunk);
  }
}

export async function pullFull(
  onProgress?: (message: string, progress?: number) => void
): Promise<boolean | 'unauthorized'> {
  const tableNames = await fetchEntityNames();
  let cursors: Record<string, number> = {};
  let hasMore = true;
  let syncedAt: string | null = null;
  let batch = 0;
  const clearedTables = new Set<string>();

  while (hasMore) {
    batch++;
    onProgress?.(`Fetching data (batch ${batch})...`, saturatingProgress(batch));

    const cursorParam =
      Object.keys(cursors).length > 0 ? `?cursor=${btoa(JSON.stringify(cursors))}` : '';

    let res: Response;
    try {
      res = await rawGet(`/api/v1/sync${cursorParam}`);
    } catch {
      return false;
    }
    if (res.status === 401) return 'unauthorized';
    if (!res.ok) return false;
    const data = (await res.json()) as FullSyncResponse;

    syncedAt = data.synced_at ?? syncedAt;

    // Stream directly into IndexedDB per batch — O(1) memory footprint
    for (const [table, rows] of Object.entries(data)) {
      if (SYNC_META_KEYS.has(table)) continue;
      if (!tableNames.has(table)) continue;
      if (rows == null) continue;

      if (!clearedTables.has(table)) {
        await db.table(table).clear();
        clearedTables.add(table);
      }

      if (isRecordArray(rows) && rows.length > 0) {
        await _bulkPutChunked(table, rows);
      } else if (typeof rows === 'object' && rows !== null && !Array.isArray(rows)) {
        await db.table(table).put(rows as Record<string, unknown>);
      }
    }

    cursors = data.cursors;
    hasMore = data.has_more;
  }

  if (syncedAt) {
    await db.meta.put({ key: 'lastSyncAt', value: new Date(syncedAt).getTime() });
  }

  return true;
}

export async function pullDelta(
  onProgress?: (message: string, progress?: number) => void
): Promise<boolean | 'unauthorized'> {
  const tableNames = await fetchEntityNames();
  const last = await db.meta.get('lastSyncAt');
  const since = last?.value as number | undefined;
  const sinceParam = since ? `?since=${new Date(since).toISOString()}` : '';

  onProgress?.('Fetching recent changes...', 0.1);

  let res: Response;
  try {
    res = await rawGet(`/api/v1/sync${sinceParam}`);
  } catch {
    return false;
  }
  if (res.status === 401) return 'unauthorized';
  if (!res.ok) return false;
  const data = (await res.json()) as DeltaResponse;

  const changedEntities = Object.entries(data.changed).filter(
    ([table, rows]) => tableNames.has(table) && isRecordArray(rows) && rows.length > 0
  );
  const deletedEntities = Object.entries(data.deleted).filter(([table]) => tableNames.has(table));
  const totalOps = changedEntities.length + deletedEntities.length;
  let opIdx = 0;

  for (const [table, rows] of changedEntities) {
    const applyProgress = totalOps > 0 ? 0.25 + (opIdx / totalOps) * 0.7 : 0.25;
    onProgress?.(`Saving ${table} (${opIdx + 1}/${totalOps})...`, applyProgress);
    await _bulkPutChunked(table, rows);
    opIdx++;
  }

  for (const [table, ids] of deletedEntities) {
    const applyProgress = totalOps > 0 ? 0.25 + (opIdx / totalOps) * 0.7 : 0.25;
    onProgress?.(`Cleaning ${table} (${opIdx + 1}/${totalOps})...`, applyProgress);
    await _bulkDeleteChunked(table, ids);
    opIdx++;
  }

  await db.meta.put({ key: 'lastSyncAt', value: new Date(data.synced_at).getTime() });

  return true;
}
