import { nativeBridge } from './bridge';
import { db } from '$lib/db/database';
import type { Measurement, OutboxOp } from '$lib/db/types';
import { syncEngine } from '$lib/db/sync-engine.svelte';

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

    // Determine since time from latest measurement with source='health_connect'
    const latest = await db.measurement
      .where('source')
      .equals('health_connect')
      .filter((m) => !m.deleted_at)
      .sortBy('start_time');

    const lastMeasuredAt = latest.length > 0 ? latest[latest.length - 1].start_time : '';

    try {
      const metrics = await nativeBridge.health.fetchDelta(lastMeasuredAt);
      if (!metrics || metrics.length === 0) {
        return {
          success: true,
          count: 0,
          message: 'Health Connect is up to date (0 new entries).'
        };
      }

      // Collect all existing external_ids in memory for O(1) deduplication
      const existingRecords = await db.measurement
        .filter((m) => m.source === 'health_connect' && !m.deleted_at)
        .toArray();
      const existingExternalIds = new Set<string>(
        existingRecords.map((r) => r.external_id).filter(Boolean) as string[]
      );

      const newMeasurements: Measurement[] = [];
      const newOutboxOps: OutboxOp[] = [];
      const nowIso = new Date().toISOString();

      for (const item of metrics) {
        if (item.external_id && existingExternalIds.has(item.external_id)) {
          continue;
        }

        const id = crypto.randomUUID();
        const measurementData: Measurement = {
          id,
          user_id: '',
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

        newOutboxOps.push({
          kind: 'crud',
          opType: 'create',
          entity: 'measurement',
          client_id: crypto.randomUUID(),
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

      // Atomic high-performance bulk insertion in Dexie
      await db.measurement.bulkPut(newMeasurements);
      await db.outbox.bulkPut(newOutboxOps);

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
