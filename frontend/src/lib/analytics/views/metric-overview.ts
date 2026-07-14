import { db } from '$lib/db/database';
import type { Measurement, MetricType } from '$lib/db/types';

export interface MetricOverview {
  metric_id: string;
  latest_value: string | null;
  latest_date: string | null;
  entry_count: number;
}

export async function fetchMetricOverview(): Promise<MetricOverview[]> {
  const measurements = await db.measurement.orderBy('start_time').reverse().toArray();

  const byMetric = new Map<string, Measurement[]>();
  for (const m of measurements) {
    if (m.deleted_at) continue;
    const arr = byMetric.get(m.metric_type_id) ?? [];
    arr.push(m);
    byMetric.set(m.metric_type_id, arr);
  }

  return [...byMetric.entries()].map(([metric_id, entries]) => {
    const latest = entries[0];
    return {
      metric_id,
      latest_value: latest.value_text ?? latest.value_numeric?.toString() ?? null,
      latest_date: latest.start_time.split('T')[0] ?? null,
      entry_count: entries.length
    };
  });
}

export function overviewForMetric(
  overviews: MetricOverview[],
  metricId: string
): MetricOverview | null {
  return overviews.find((o) => o.metric_id === metricId) ?? null;
}
