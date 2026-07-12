import { db } from './database';
import { getAuthHeaders } from '$lib/api/headers';

const TABLE_NAMES = new Set<string>([
  'metric_type', 'measurement', 'goal', 'circadian_profile',
  'exercise', 'workout_plan', 'workout_plan_exercise',
  'workout_session', 'workout_log_entry', 'insight',
  'notification', 'dashboard_widget', 'sharing_relationship',
  'leaderboard_group', 'leaderboard_member',
  'share_recipient', 'asymmetric_share',
  'user_profile', 'admin_user', 'admin_stats', 'system_config',
  'api_token', 'user', 'community_activity', 'federated_access_log',
]);

const SYNC_META_KEYS = new Set([
  'cursors', 'has_more', 'synced_at',
]);

async function apiGet<T>(url: string): Promise<{ data: T | null; status: number }> {
  const headers = { ...getAuthHeaders(), Accept: 'application/json' };

  const res = await fetch(url, { headers });
  if (!res.ok) return { data: null, status: res.status };
  return { data: (await res.json()) as T, status: res.status };
}

function isRecordArray(value: unknown): value is Record<string, unknown>[] {
  return Array.isArray(value);
}

interface FullSyncResponse {
  cursors: Record<string, number>;
  has_more: boolean;
  synced_at: string;
  [table: string]: unknown;
}

export async function pullFull(): Promise<boolean | 'unauthorized'> {
  let cursors: Record<string, number> = {};
  let hasMore = true;
  const allRows: Record<string, Record<string, unknown>[]> = {};
  let syncedAt: string | null = null;

  while (hasMore) {
    const cursorParam = Object.keys(cursors).length > 0
      ? `?cursor=${btoa(JSON.stringify(cursors))}`
      : '';
    const { data, status } = await apiGet<FullSyncResponse>(`/api/v1/sync${cursorParam}`);

    if (status === 401) return 'unauthorized';
    if (!data) return false;

    syncedAt = data.synced_at ?? syncedAt;

    for (const [table, rows] of Object.entries(data)) {
      if (SYNC_META_KEYS.has(table)) continue;
      if (!TABLE_NAMES.has(table)) continue;
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

  await db.transaction('rw', db.tables, async () => {
    for (const [table, rows] of Object.entries(allRows)) {
      await db.table(table).clear();

      if (rows.length > 0) {
        const first = rows[0];
        if (first && typeof first === 'object' && !Array.isArray(first)) {
          await db.table(table).bulkPut(rows);
        }
      }
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

export async function pullDelta(): Promise<boolean | 'unauthorized'> {
  const last = await db.meta.get('lastSyncAt');
  const since = last?.value as number | undefined;
  const sinceParam = since ? `?since=${new Date(since).toISOString()}` : '';

  const { data, status } = await apiGet<DeltaResponse>(`/api/v1/sync${sinceParam}`);
  if (status === 401) return 'unauthorized';
  if (!data) return false;

  await db.transaction('rw', db.tables, async () => {
    for (const [table, rows] of Object.entries(data.changed)) {
      if (!TABLE_NAMES.has(table) || !isRecordArray(rows) || rows.length === 0) continue;
      await db.table(table).bulkPut(rows);
    }
    for (const [table, ids] of Object.entries(data.deleted)) {
      if (!TABLE_NAMES.has(table)) continue;
      await db.table(table).bulkDelete(ids);
    }
    await db.meta.put({ key: 'lastSyncAt', value: new Date(data.synced_at).getTime() });
  });

  return true;
}
