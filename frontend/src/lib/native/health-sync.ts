import { nativeBridge } from './bridge';
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

export const healthSyncService = {
  async isAvailable(): Promise<boolean> {
    return nativeBridge.health.isAvailable();
  },

  async checkPermissions(): Promise<{ granted: boolean; missing: string[] }> {
    const res = await nativeBridge.health.checkPermissions();
    return {
      granted: res.granted,
      missing: res.missingPermissions
    };
  },

  async requestPermissions(): Promise<boolean> {
    return nativeBridge.health.requestPermissions();
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

    // Determine since time from meta store or latest measurement
    const metaSync = await db.meta.get('health_connect:last_sync');
    let lastMeasuredAt = (metaSync?.value as string) ?? '';

    if (!lastMeasuredAt) {
      const latest = await db.measurement
        .where('start_time')
        .above('')
        .filter((m) => m.source === 'health_connect' && !m.deleted_at)
        .last();
      lastMeasuredAt = latest?.start_time ?? '';
    }

    try {
      const metrics = await nativeBridge.health.fetchDelta(lastMeasuredAt);
      if (!metrics || metrics.length === 0) {
        return {
          success: true,
          count: 0,
          message: 'Health Connect is up to date (0 new entries).'
        };
      }

      // Check only incoming external IDs against indexedDB external_id index
      const incomingExternalIds = metrics.map((m) => m.external_id).filter(Boolean);
      const existingInDb =
        incomingExternalIds.length > 0
          ? await db.measurement.where('external_id').anyOf(incomingExternalIds).toArray()
          : [];
      const existingExternalIds = new Set<string>(
        existingInDb.map((r) => r.external_id).filter(Boolean) as string[]
      );

      const newMeasurements: Measurement[] = [];
      const newOutboxOps: OutboxOp[] = [];
      const nowIso = new Date().toISOString();
      let maxMeasuredAt = lastMeasuredAt;

      for (const item of metrics) {
        if (item.external_id && existingExternalIds.has(item.external_id)) {
          continue;
        }

        const id = uuid7();
        const measurementData: Measurement = {
          id,
          user_id: SELF_USER_ID,
          metric_code: item.metric_code,
          data_type: 'number',
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
          existingExternalIds.add(item.external_id);
        }
        if (item.measured_at && item.measured_at > maxMeasuredAt) {
          maxMeasuredAt = item.measured_at;
        }

        newOutboxOps.push({
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

      // Atomic bulk insertion in Dexie
      await db.measurement.bulkPut(newMeasurements);
      await db.outbox.bulkPut(newOutboxOps);
      if (maxMeasuredAt) {
        await db.meta.put({ key: 'health_connect:last_sync', value: maxMeasuredAt });
      }

      if (newMeasurements.length > 0) {
        await recomputeAllStats();
      }

      // Trigger asynchronous background flush to server without blocking UI
      syncEngine.flush().catch((e) => console.error('Outbox flush error:', e));

      return {
        success: true,
        count: newMeasurements.length,
        message: `Successfully synchronized ${newMeasurements.length} measurements from Health Connect.`
      };
    } catch (e: unknown) {
      const err = e instanceof Error ? e.message : String(e);
      return { success: false, count: 0, message: `Health Connect sync failed: ${err}` };
    }
  }
};
