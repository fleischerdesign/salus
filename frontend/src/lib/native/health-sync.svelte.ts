import { nativeBridge } from './bridge';
import type { IngestedMetricPayload } from './types';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';
import { db } from '$lib/db/database';
import type { Measurement } from '$lib/db/types';
import { recomputeAllStats } from '$lib/db/metric-stats';
import { localMode } from '$lib/db/local-mode.svelte';
import { api } from '$lib/api/client';

export interface HealthSyncResult {
  success: boolean;
  count: number;
  message: string;
}

export interface HealthPermissionState {
  granted: boolean;
  missing: string[];
  grantedPermissions: string[];
}

const CHANGES_TOKEN_KEY = 'health_connect:changes_token';
const CHANGES_GRANTED_KEY = 'health_connect:changes_granted';
const LAST_SYNC_KEY = 'health_connect:last_sync';
const LAST_PUSHED_KEY = 'health_connect:last_pushed';
const BATCH = 500;

/**
 * Live progress of the one-time history import (null when idle). Exported as a mutable
 * object so components read it reactively without reassigning the exported binding.
 */
export const healthSyncUi = $state<{ seedProgress: { done: number } | null }>({
  seedProgress: null
});

export function permissionLabel(permission: string): string {
  return permission
    .replace(/^android\.permission\.health\.READ_/, '')
    .replace(/_/g, ' ')
    .toLowerCase();
}

export const healthSyncService = {
  async isAvailable(): Promise<boolean> {
    return nativeBridge.health.isAvailable();
  },

  async checkPermissions(): Promise<HealthPermissionState> {
    const res = await nativeBridge.health.checkPermissions();
    return {
      granted: res.granted,
      missing: res.missingPermissions,
      grantedPermissions: res.grantedPermissions ?? []
    };
  },

  async requestPermissions(): Promise<boolean> {
    return nativeBridge.health.requestPermissions();
  },

  async openHealthConnectSettings(): Promise<boolean> {
    return nativeBridge.health.openSettings();
  },

  async grantedSignature(): Promise<string> {
    const res = await nativeBridge.health.checkPermissions();
    return [...(res.grantedPermissions ?? [])].sort().join(',');
  },

  async syncNow(): Promise<HealthSyncResult> {
    const isAvail = await nativeBridge.health.isAvailable();
    if (!isAvail) {
      return {
        success: false,
        count: 0,
        message: 'Health Connect is not available on this platform.'
      };
    }

    try {
      // The changes API requires a read permission for every record type it covers, so a probe
      // returns null when it is unusable (e.g. no permission granted at all). Degrade to a
      // bounded time-based delta instead of a full-history scan.
      const probe = await nativeBridge.health.getChangesToken();
      if (!probe) {
        const lastSync = await db.meta.get(LAST_SYNC_KEY);
        const cursor = typeof lastSync?.value === 'string' ? lastSync.value : '';
        let fetchCursor: string | null = null;
        let count = 0;
        do {
          const batch = await nativeBridge.health.fetchDelta(cursor, fetchCursor);
          count += await ingestMetrics(batch.metrics, cursor);
          fetchCursor = batch.nextCursor || null;
        } while (fetchCursor);
        void pushUnsyncedHealth();
        return syncResult(count);
      }

      const grantedSignature = await this.grantedSignature();
      const storedToken = await db.meta.get(CHANGES_TOKEN_KEY);
      const storedValue = typeof storedToken?.value === 'string' ? storedToken.value : '';
      const storedGranted = (await db.meta.get(CHANGES_GRANTED_KEY))?.value;

      if (!storedValue || storedGranted !== grantedSignature) {
        // First run, or the granted permission set changed (e.g. after re-authorizing):
        // import the full history in the background so the UI never blocks.
        return startSeed(probe, grantedSignature);
      }

      const result = await nativeBridge.health.getChanges(storedValue);
      if (result.nextToken) {
        await db.meta.put({ key: CHANGES_TOKEN_KEY, value: result.nextToken });
        const count = await ingestMetrics(result.metrics, storedValue);
        void pushUnsyncedHealth();
        return syncResult(count);
      }

      // Stale or expired token: re-pin a fresh baseline and re-import in the background.
      return startSeed(probe, grantedSignature);
    } catch (e: unknown) {
      const err = e instanceof Error ? e.message : String(e);
      return { success: false, count: 0, message: `Health Connect sync failed: ${err}` };
    }
  }
};

function syncResult(count: number): HealthSyncResult {
  return count > 0
    ? {
        success: true,
        count,
        message: `Successfully synchronized ${count} measurements from Health Connect.`
      }
    : { success: true, count: 0, message: 'Health Connect is up to date (0 new entries).' };
}

function startSeed(token: string, grantedSignature: string): HealthSyncResult {
  if (healthSyncUi.seedProgress) {
    return {
      success: true,
      count: 0,
      message: 'Health Connect history is already importing in the background.'
    };
  }
  healthSyncUi.seedProgress = { done: 0 };
  void (async () => {
    try {
      let cursor: string | null = null;
      let done = 0;
      do {
        const batch = await nativeBridge.health.fetchDelta('', cursor);
        done += await ingestMetrics(batch.metrics, '');
        healthSyncUi.seedProgress = { done };
        cursor = batch.nextCursor || null;
      } while (cursor);
      // Pin the baseline only after a successful import so a mid-seed failure leaves the
      // cursor unset — the next sync re-seeds and dedup skips what already landed.
      await db.meta.put({ key: CHANGES_TOKEN_KEY, value: token });
      await db.meta.put({ key: CHANGES_GRANTED_KEY, value: grantedSignature });
    } catch (e) {
      console.error('Health Connect history import failed:', e);
    } finally {
      healthSyncUi.seedProgress = null;
      void pushUnsyncedHealth();
    }
  })();
  return {
    success: true,
    count: 0,
    message: 'Seeding Health Connect history in the background — you can keep using the app.'
  };
}

/** Chunked, outbox-free ingestion of harvested metrics into Dexie. */
async function ingestMetrics(
  metrics: IngestedMetricPayload[],
  lastMeasuredAt: string
): Promise<number> {
  if (!metrics || metrics.length === 0) return 0;

  const nowIso = new Date().toISOString();
  let maxMeasuredAt = lastMeasuredAt;
  let count = 0;
  // Carried across batches so a duplicate external_id spanning a batch boundary is caught.
  const seenById = new Map<string, Measurement>();

  for (let i = 0; i < metrics.length; i += BATCH) {
    const chunk = metrics.slice(i, i + BATCH);
    const result = await ingestChunk(chunk, nowIso, seenById);
    count += result.count;
    if (result.maxMeasuredAt > maxMeasuredAt) maxMeasuredAt = result.maxMeasuredAt;
    await yieldToEventLoop();
  }

  if (maxMeasuredAt) {
    await db.meta.put({ key: LAST_SYNC_KEY, value: maxMeasuredAt });
  }
  if (count > 0) {
    await recomputeAllStats();
  }
  return count;
}

async function ingestChunk(
  chunk: IngestedMetricPayload[],
  nowIso: string,
  seenById: Map<string, Measurement>
): Promise<{ count: number; maxMeasuredAt: string }> {
  const incomingExternalIds = chunk.map((m) => m.external_id).filter(Boolean);
  const existingInDb =
    incomingExternalIds.length > 0
      ? await db.measurement.where('external_id').anyOf(incomingExternalIds).toArray()
      : [];
  for (const row of existingInDb) {
    if (row.external_id && !seenById.has(row.external_id)) {
      seenById.set(row.external_id, row);
    }
  }

  const writes: Measurement[] = [];
  let maxMeasuredAt = '';

  for (const item of chunk) {
    const existing = item.external_id ? seenById.get(item.external_id) : undefined;
    if (existing) {
      // Edited record: propagate value/time changes to the local measurement.
      const changed =
        existing.value_numeric !== (item.value ?? null) ||
        existing.value_text !== (item.value_text ?? null) ||
        existing.value_json !== (item.value_json ?? null) ||
        existing.start_time !== item.measured_at;
      if (changed) {
        const updated: Measurement = {
          ...existing,
          value_numeric: item.value ?? null,
          value_text: item.value_text ?? null,
          value_json: item.value_json ?? null,
          start_time: item.measured_at,
          end_time: item.end_time ?? existing.end_time,
          updated_at: nowIso
        };
        writes.push(updated);
        seenById.set(item.external_id as string, updated);
      }
    } else {
      const measurement: Measurement = {
        id: uuid7(),
        user_id: SELF_USER_ID,
        metric_code: item.metric_code,
        source_data_type: '',
        value_numeric: item.value ?? null,
        value_text: item.value_text ?? null,
        value_json: item.value_json ?? null,
        start_time: item.measured_at,
        end_time: item.end_time ?? item.measured_at,
        source: 'health_connect',
        external_id: item.external_id,
        notes: null,
        created_at: nowIso,
        updated_at: nowIso,
        deleted_at: null
      };
      writes.push(measurement);
      if (item.external_id) {
        seenById.set(item.external_id, measurement);
      }
    }
    if (item.measured_at && item.measured_at > maxMeasuredAt) {
      maxMeasuredAt = item.measured_at;
    }
  }

  if (writes.length > 0) {
    await db.measurement.bulkPut(writes);
  }
  return { count: writes.length, maxMeasuredAt };
}

function yieldToEventLoop(): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

/** Bulk-replicate unsynced health measurements to the server (idempotent by external_id). */
async function pushUnsyncedHealth(): Promise<void> {
  if (localMode.active) return;
  if (typeof navigator !== 'undefined' && !navigator.onLine) return;

  const watermark = (await db.meta.get(LAST_PUSHED_KEY))?.value as string | undefined;
  const unsynced = await db.measurement
    .where('source')
    .equals('health_connect')
    .filter((m) => !m.deleted_at && (!watermark || (m.updated_at ?? m.created_at) > watermark))
    .sortBy('updated_at');
  if (unsynced.length === 0) return;

  for (let i = 0; i < unsynced.length; i += BATCH) {
    const chunk = unsynced.slice(i, i + BATCH);
    if (!(await pushMeasurements(chunk))) return;
    const maxUpdated = chunk.reduce<string>(
      (max, m) => ((m.updated_at ?? m.created_at) > max ? (m.updated_at ?? m.created_at) : max),
      ''
    );
    if (maxUpdated) {
      await db.meta.put({ key: LAST_PUSHED_KEY, value: maxUpdated });
    }
  }
}

async function pushMeasurements(measurements: Measurement[]): Promise<boolean> {
  try {
    const res = await api.POST('/api/v1/sync/health-push', {
      body: {
        measurements: measurements.map((m) => ({
          id: m.id,
          metric_code: m.metric_code ?? '',
          source_data_type: m.source_data_type,
          source: m.source,
          value_numeric: m.value_numeric,
          value_text: m.value_text,
          value_json: m.value_json,
          start_time: m.start_time,
          end_time: m.end_time,
          external_id: m.external_id,
          created_at: m.created_at,
          updated_at: m.updated_at
        }))
      }
    });
    return res.response.ok;
  } catch {
    return false;
  }
}
