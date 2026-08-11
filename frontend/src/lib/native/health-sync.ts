import { nativeBridge } from './bridge';
import { db } from '$lib/db/database';
import { mutate } from '$lib/mutate';
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
      return { success: false, count: 0, message: 'Health Connect is not available on this platform.' };
    }

    // Determine since time from latest measurement with source='health_connect'
    const latest = await db.measurement
      .filter((m) => m.source === 'health_connect' && !m.deleted_at)
      .sortBy('measured_at');

    const lastMeasuredAt = latest.length > 0 ? latest[latest.length - 1].measured_at : '';

    try {
      const metrics = await nativeBridge.health.fetchDelta(lastMeasuredAt);
      if (!metrics || metrics.length === 0) {
        return { success: true, count: 0, message: 'Health Connect is up to date (0 new entries).' };
      }

      let inserted = 0;
      for (const item of metrics) {
        // Check if measurement with same external_id already exists in Dexie
        if (item.external_id) {
          const existing = await db.measurement
            .filter((m) => m.external_id === item.external_id && !m.deleted_at)
            .first();
          if (existing) continue;
        }

        const id = crypto.randomUUID();
        await mutate({
          kind: 'crud',
          op: 'create',
          entity: 'measurement',
          id,
          data: {
            id,
            metric_code: item.metric_code,
            data_type: 'number',
            value_numeric: item.value,
            value_text: null,
            value_boolean: null,
            unit: item.unit,
            measured_at: item.measured_at,
            source: 'health_connect',
            external_id: item.external_id,
            notes: null,
            created_at: new Date().toISOString()
          }
        });
        inserted++;
      }

      // Trigger immediate background outbox push to Salus server
      syncEngine.flush().catch((e) => console.error('Outbox flush error:', e));

      return {
        success: true,
        count: inserted,
        message: `Successfully synchronized ${inserted} measurements from Health Connect.`
      };
    } catch (e: unknown) {
      const err = e instanceof Error ? e.message : String(e);
      return { success: false, count: 0, message: `Health Connect sync failed: ${err}` };
    }
  }
};
