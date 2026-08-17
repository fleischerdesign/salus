import { db } from './database';
import type { Measurement } from './types';
import {
  applyDailyDeltas,
  measurementDailyDelta,
  rebuildMetricDailyCache,
  type DailyDelta
} from './daily-stats';
import { userTimezone } from '$lib/utils/timezone';

/**
 * Single write path for measurement rows. Keeps the measurement table and the
 * per-day aggregate cache consistent in one atomic transaction.
 *
 * All measurement writes — user edits (mutate), server pulls (sync-pull), the
 * Health Connect ingest and the backup import — MUST route through this module;
 * that is what makes the derived cache deterministic.
 */

export async function createMeasurements(records: Measurement[]): Promise<void> {
  if (records.length === 0) return;
  const tz = userTimezone();
  const deltas = records.flatMap((m) => measurementDailyDelta(tz, m));
  await db.transaction('rw', db.measurement, db.metric_daily_stats, async () => {
    await db.measurement.bulkPut(records);
    await applyDailyDeltas(deltas);
  });
}

export async function updateMeasurements(records: Measurement[]): Promise<void> {
  if (records.length === 0) return;
  const tz = userTimezone();
  await db.transaction('rw', db.measurement, db.metric_daily_stats, async () => {
    const deltas: DailyDelta[] = [];
    for (const m of records) {
      const existing = await db.measurement.get(m.id);
      if (!existing) continue;
      deltas.push(...measurementDailyDelta(tz, m, existing));
    }
    await db.measurement.bulkPut(records);
    await applyDailyDeltas(deltas);
  });
}

/** Create-or-update: adjusts the cache from each row's prior state if it exists. */
export async function upsertMeasurements(records: Measurement[]): Promise<void> {
  if (records.length === 0) return;
  const tz = userTimezone();
  await db.transaction('rw', db.measurement, db.metric_daily_stats, async () => {
    const deltas: DailyDelta[] = [];
    for (const m of records) {
      const existing = await db.measurement.get(m.id);
      deltas.push(...measurementDailyDelta(tz, m, existing));
    }
    await db.measurement.bulkPut(records);
    await applyDailyDeltas(deltas);
  });
}

export async function deleteMeasurements(ids: string[]): Promise<void> {
  if (ids.length === 0) return;
  const tz = userTimezone();
  await db.transaction('rw', db.measurement, db.metric_daily_stats, async () => {
    const deltas: DailyDelta[] = [];
    for (const id of ids) {
      const existing = await db.measurement.get(id);
      if (!existing) continue;
      deltas.push(
        ...measurementDailyDelta(
          tz,
          {
            metric_code: existing.metric_code,
            start_time: existing.start_time,
            value_numeric: null,
            deleted_at: 'deleted'
          },
          existing
        )
      );
    }
    await db.measurement.bulkDelete(ids);
    await applyDailyDeltas(deltas);
  });
}

/** Bulk restore (import/seed): replace all measurements and rebuild the affected caches. */
export async function restoreMeasurements(records: Measurement[]): Promise<void> {
  const codes = new Set(records.map((m) => m.metric_code).filter(Boolean) as string[]);
  await db.transaction('rw', db.measurement, db.metric_daily_stats, async () => {
    await db.measurement.clear();
    await db.metric_daily_stats.clear();
    if (records.length > 0) await db.measurement.bulkPut(records);
  });
  for (const code of codes) {
    await rebuildMetricDailyCache(code);
  }
}
