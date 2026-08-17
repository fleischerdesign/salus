import Dexie from 'dexie';
import { db } from './database';
import type { MetricDailyStat } from './types';
import { userTimezone } from '$lib/utils/timezone';
import { aggregateDailyDeltas, measurementDay, type DailyDelta } from './daily-stats-core';

export { measurementDailyDelta, aggregateDailyDeltas, type DailyDelta } from './daily-stats-core';

/**
 * Per-day numeric aggregates for the trend charts. A device-local derived cache,
 * maintained incrementally by the measurement write facade and rebuilt lazily on
 * first view / after bulk writes (import, seed). Never synced.
 *
 * Maintenance contract: the write facade is the single path that mutates
 * measurements, so the cache is deterministic by construction (count/sum over
 * non-deleted rows). `rebuildMetricDailyCache` exists for backfill and repair.
 */

/** Apply bucket adjustments to the cache, dropping days whose count reached zero. */
export async function applyDailyDeltas(deltas: DailyDelta[]): Promise<void> {
  const buckets = aggregateDailyDeltas(deltas);
  for (const delta of buckets.values()) {
    const key: [string, string] = [delta.metric_code, delta.day];
    const existing = await db.metric_daily_stats.get(key);
    const count = (existing?.count ?? 0) + delta.count;
    const sum = (existing?.sum ?? 0) + delta.sum;
    if (count <= 0) {
      if (existing) await db.metric_daily_stats.delete(key);
    } else {
      await db.metric_daily_stats.put({
        metric_code: delta.metric_code,
        day: delta.day,
        count,
        sum
      });
    }
  }
}

/** Per-day means for a metric in `[fromDay, toDay]` (inclusive), oldest first. */
export async function fetchDailyMeans(
  code: string,
  fromDay: string,
  toDay: string
): Promise<Array<{ day: string; count: number; mean: number }>> {
  // Code-bounded range (between with maxKey upper) plus a JS day filter — a plain
  // aboveOrEqual would bleed into every lexicographically larger metric, and Dexie's
  // between() upper bound is unreliable for the exact upper day.
  const rows = await db.metric_daily_stats
    .where('[metric_code+day]')
    .between([code, fromDay], [code, Dexie.maxKey])
    .filter((r) => r.day <= toDay)
    .toArray();
  const out: Array<{ day: string; count: number; mean: number }> = [];
  for (const row of rows) {
    if (row.count > 0) out.push({ day: row.day, count: row.count, mean: row.sum / row.count });
  }
  return out;
}

/** Streamed rebuild of one metric's cache from raw rows (background repair/backfill). */
export async function rebuildMetricDailyCache(code: string): Promise<void> {
  const tz = userTimezone();
  const buckets = new Map<string, MetricDailyStat>();
  await db.measurement
    .where('[metric_code+start_time]')
    .between([code, Dexie.minKey], [code, Dexie.maxKey])
    .each((m) => {
      if (m.deleted_at || m.value_numeric == null) return;
      const day = measurementDay(m.start_time, tz);
      const key = `${code}:${day}`;
      const b = buckets.get(key) ?? { metric_code: code, day, count: 0, sum: 0 };
      b.count += 1;
      b.sum += m.value_numeric;
      buckets.set(key, b);
    });

  await db.transaction('rw', db.metric_daily_stats, async () => {
    await db.metric_daily_stats.where('metric_code').equals(code).delete();
    if (buckets.size > 0) {
      await db.metric_daily_stats.bulkPut([...buckets.values()]);
    }
  });
}
