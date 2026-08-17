import { dateStringInTz } from '$lib/utils/timezone';
import type { MetricDailyStat } from './types';

/**
 * Pure day-bucket arithmetic for the measurement daily-aggregate cache.
 * Kept free of any Dexie/IndexedDB dependency so it is directly unit-testable.
 */

/** One per-day bucket adjustment for a measurement write. */
export interface DailyDelta {
  metric_code: string;
  day: string;
  count: number;
  sum: number;
}

/** Local `YYYY-MM-DD` day string for an instant in the user's timezone (ADR-009). */
export function measurementDay(iso: string, tz: string): string {
  return dateStringInTz(iso, tz);
}

export type NumericMeasurement = {
  metric_code: string | null;
  start_time: string;
  value_numeric: number | null;
  deleted_at?: string | null;
};

/**
 * The day-bucket adjustments for a measurement write. `before` carries the prior
 * state for updates/deletes so the old bucket is decremented and (for updates)
 * the value/day change is applied. Soft-deleted rows add nothing.
 */
export function measurementDailyDelta(
  tz: string,
  m: NumericMeasurement,
  before?: { start_time: string; value_numeric: number | null } | null
): DailyDelta[] {
  const code = m.metric_code;
  if (!code) return [];
  const deltas: DailyDelta[] = [];

  if (before) {
    if (before.value_numeric != null) {
      deltas.push({
        metric_code: code,
        day: measurementDay(before.start_time, tz),
        count: -1,
        sum: -before.value_numeric
      });
    }
  }

  const value = m.deleted_at ? null : m.value_numeric;
  if (value != null) {
    deltas.push({ metric_code: code, day: measurementDay(m.start_time, tz), count: 1, sum: value });
  }

  return deltas;
}

/** Merge per-measurement deltas into per-day buckets. */
export function aggregateDailyDeltas(deltas: DailyDelta[]): Map<string, MetricDailyStat> {
  const buckets = new Map<string, MetricDailyStat>();
  for (const d of deltas) {
    const key = `${d.metric_code}:${d.day}`;
    const b = buckets.get(key) ?? { metric_code: d.metric_code, day: d.day, count: 0, sum: 0 };
    b.count += d.count;
    b.sum += d.sum;
    buckets.set(key, b);
  }
  return buckets;
}
