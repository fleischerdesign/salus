import { db } from '$lib/db/database';
import type { Measurement } from '$lib/db/types';

export interface MetricOverview {
  metric_id: string;
  latest_value: string | null;
  latest_date: string | null;
  entry_count: number;
}

export async function fetchMetricOverview(): Promise<MetricOverview[]> {
  const defs = await db.metric_definition.toArray();
  if (defs.length === 0) return [];

  const results = await Promise.all(
    defs.map(async (def) => {
      const count = await db.measurement
        .where('metric_code')
        .equals(def.code)
        .filter((m) => !m.deleted_at)
        .count();

      if (count === 0) return null;

      const latest = await db.measurement
        .where('metric_code')
        .equals(def.code)
        .filter((m) => !m.deleted_at)
        .reverse()
        .sortBy('start_time')
        .then((arr) => (arr.length > 0 ? arr[arr.length - 1] : null));

      return {
        metric_id: def.code,
        latest_value: latest?.value_text ?? latest?.value_numeric?.toString() ?? null,
        latest_date: latest?.start_time ? latest.start_time.split('T')[0] : null,
        entry_count: count
      };
    })
  );

  return results.filter((o): o is MetricOverview => o !== null);
}

export function overviewForMetric(
  overviews: MetricOverview[],
  metricId: string
): MetricOverview | null {
  return overviews.find((o) => o.metric_id === metricId) ?? null;
}
