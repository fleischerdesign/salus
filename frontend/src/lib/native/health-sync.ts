import { nativeBridge } from './bridge';
import type { IngestedMetricPayload } from './types';
import { SELF_USER_ID } from '$lib/constants';
import { uuid7 } from '$lib/db/uuid';
import { db } from '$lib/db/database';
import type { Measurement, OutboxOp } from '$lib/db/types';
import { syncEngine } from '$lib/db/sync-engine.svelte';
import { recomputeAllStats } from '$lib/db/metric-stats';

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
const LAST_SYNC_KEY = 'health_connect:last_sync';

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
      // Incremental path: the Health Connect change token is the sync cursor.
      const storedToken = await db.meta.get(CHANGES_TOKEN_KEY);
      const storedValue = storedToken?.value;
      if (typeof storedValue === 'string' && storedValue) {
        const result = await nativeBridge.health.getChanges(storedValue);
        if (result.nextToken) {
          await db.meta.put({ key: CHANGES_TOKEN_KEY, value: result.nextToken });
          return ingestMetrics(result.metrics, storedValue);
        }
        // Stale or expired token: re-pin a fresh baseline and reseed the history.
        const freshToken = await nativeBridge.health.getChangesToken();
        if (!freshToken) {
          return {
            success: false,
            count: 0,
            message:
              'Health Connect change tracking is unavailable. Grant the "Health data history" permission and try again.'
          };
        }
        await db.meta.put({ key: CHANGES_TOKEN_KEY, value: freshToken });
        const reseedMetrics = await nativeBridge.health.fetchDelta('');
        return ingestMetrics(reseedMetrics, '');
      }

      // First run: seed the full history once, then pin the change token as baseline.
      const seedMetrics = await nativeBridge.health.fetchDelta('');
      const baselineToken = await nativeBridge.health.getChangesToken();
      if (baselineToken) {
        await db.meta.put({ key: CHANGES_TOKEN_KEY, value: baselineToken });
      }
      return ingestMetrics(seedMetrics, '');
    } catch (e: unknown) {
      const err = e instanceof Error ? e.message : String(e);
      return { success: false, count: 0, message: `Health Connect sync failed: ${err}` };
    }
  }
};

async function ingestMetrics(
  metrics: IngestedMetricPayload[],
  lastMeasuredAt: string
): Promise<HealthSyncResult> {
  if (!metrics || metrics.length === 0) {
    return {
      success: true,
      count: 0,
      message: 'Health Connect is up to date (0 new entries).'
    };
  }

  const incomingExternalIds = metrics.map((m) => m.external_id).filter(Boolean);
  const existingInDb =
    incomingExternalIds.length > 0
      ? await db.measurement.where('external_id').anyOf(incomingExternalIds).toArray()
      : [];
  const existingById = new Map<string, Measurement>(
    existingInDb.filter((r) => r.external_id).map((r) => [r.external_id as string, r])
  );

  const newMeasurements: Measurement[] = [];
  const outboxOps: OutboxOp[] = [];
  const nowIso = new Date().toISOString();
  let maxMeasuredAt = lastMeasuredAt;

  for (const item of metrics) {
    const existing = item.external_id ? existingById.get(item.external_id) : undefined;
    if (existing) {
      // Edited record: propagate the value/time change to the local measurement.
      if (existing.value_numeric !== item.value || existing.start_time !== item.measured_at) {
        const updated: Measurement = {
          ...existing,
          value_numeric: item.value,
          start_time: item.measured_at,
          end_time: item.measured_at,
          updated_at: nowIso
        };
        newMeasurements.push(updated);
        outboxOps.push({
          kind: 'crud',
          opType: 'update',
          entity: 'measurement',
          client_id: uuid7(),
          data: updated as unknown as Record<string, unknown>,
          realId: existing.id,
          createdAt: nowIso,
          retries: 0
        });
      }
      if (item.measured_at && item.measured_at > maxMeasuredAt) {
        maxMeasuredAt = item.measured_at;
      }
      continue;
    }

    const id = uuid7();
    const measurementData: Measurement = {
      id,
      user_id: SELF_USER_ID,
      metric_code: item.metric_code,
      source_data_type: '',
      value_numeric: item.value,
      value_text: null,
      value_json: null,
      start_time: item.measured_at,
      end_time: item.measured_at,
      source: 'health_connect',
      external_id: item.external_id,
      notes: null,
      created_at: nowIso,
      updated_at: nowIso,
      deleted_at: null
    };

    newMeasurements.push(measurementData);
    if (item.external_id) {
      existingById.set(item.external_id, measurementData);
    }
    if (item.measured_at && item.measured_at > maxMeasuredAt) {
      maxMeasuredAt = item.measured_at;
    }

    outboxOps.push({
      kind: 'crud',
      opType: 'create',
      entity: 'measurement',
      client_id: uuid7(),
      data: measurementData as unknown as Record<string, unknown>,
      realId: id,
      createdAt: nowIso,
      retries: 0
    });
  }

  if (newMeasurements.length === 0) {
    return {
      success: true,
      count: 0,
      message: 'All Health Connect entries already exist locally.'
    };
  }

  await db.measurement.bulkPut(newMeasurements);
  await db.outbox.bulkPut(outboxOps);
  if (maxMeasuredAt) {
    await db.meta.put({ key: LAST_SYNC_KEY, value: maxMeasuredAt });
  }
  await recomputeAllStats();
  syncEngine.flush().catch((e) => console.error('Outbox flush error:', e));

  return {
    success: true,
    count: newMeasurements.length,
    message: `Successfully synchronized ${newMeasurements.length} measurements from Health Connect.`
  };
}
