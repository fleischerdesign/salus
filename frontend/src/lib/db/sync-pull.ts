import { db } from './database';
import { rawGet } from '$lib/api/client';
import { fetchEntityNames } from './entity-info';

const SYNC_META_KEYS = new Set([
  'cursors', 'has_more', 'synced_at',
]);

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

export async function pullFull(
  onProgress?: (message: string, progress?: number) => void,
): Promise<boolean | 'unauthorized'> {
  const tableNames = await fetchEntityNames();
  let cursors: Record<string, number> = {};
  let hasMore = true;
  const allRows: Record<string, Record<string, unknown>[]> = {};
  let syncedAt: string | null = null;
  let batch = 0;

  while (hasMore) {
    batch++;
    onProgress?.(`Fetching data (batch ${batch})...`, saturatingProgress(batch));

    const cursorParam = Object.keys(cursors).length > 0
      ? `?cursor=${btoa(JSON.stringify(cursors))}`
      : '';

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

    for (const [table, rows] of Object.entries(data)) {
      if (SYNC_META_KEYS.has(table)) continue;
      if (!tableNames.has(table)) continue;
      if (rows == null) continue;

      if (!allRows[table]) allRows[table] = [];

      if (isRecordArray(rows)) {
        allRows[table].push(...rows);
      } else if (typeof rows === 'object') {
        allRows[table].push(rows as Record<string, unknown>);
      }
    }

    cursors = data.cursors;
    hasMore = data.has_more;
  }

  const entities = Object.keys(allRows);
  const total = entities.length;
  let idx = 0;

  await db.transaction('rw', db.tables, async () => {
    for (const [table, rows] of Object.entries(allRows)) {
      const applyProgress = total > 0 ? 0.6 + (idx / total) * 0.35 : 0.6;
      onProgress?.(`Saving ${table} (${idx + 1}/${total})...`, applyProgress);

      await db.table(table).clear();

      if (rows.length > 0) {
        const first = rows[0];
        if (first && typeof first === 'object' && !Array.isArray(first)) {
          await db.table(table).bulkPut(rows);
        }
      }

      idx++;
    }

    if (syncedAt) {
      await db.meta.put({ key: 'lastSyncAt', value: new Date(syncedAt).getTime() });
    }
  });

  return true;
}

interface DeltaResponse {
  changed: Record<string, Record<string, unknown>[]>;
  deleted: Record<string, number[]>;
  synced_at: string;
}

export async function pullDelta(
  onProgress?: (message: string, progress?: number) => void,
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
    ([table, rows]) => tableNames.has(table) && isRecordArray(rows) && rows.length > 0,
  );
  const deletedEntities = Object.entries(data.deleted).filter(
    ([table]) => tableNames.has(table),
  );
  const totalOps = changedEntities.length + deletedEntities.length;
  let opIdx = 0;

  await db.transaction('rw', db.tables, async () => {
    for (const [table, rows] of changedEntities) {
      const applyProgress = totalOps > 0 ? 0.25 + (opIdx / totalOps) * 0.7 : 0.25;
      onProgress?.(`Saving ${table} (${opIdx + 1}/${totalOps})...`, applyProgress);
      await db.table(table).bulkPut(rows);
      opIdx++;
    }

    for (const [table, ids] of deletedEntities) {
      const applyProgress = totalOps > 0 ? 0.25 + (opIdx / totalOps) * 0.7 : 0.25;
      onProgress?.(`Cleaning ${table} (${opIdx + 1}/${totalOps})...`, applyProgress);
      await db.table(table).bulkDelete(ids);
      opIdx++;
    }

    await db.meta.put({ key: 'lastSyncAt', value: new Date(data.synced_at).getTime() });
  });

  return true;
}
