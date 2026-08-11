import Dexie from 'dexie';
import { db } from '$lib/db/database';

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
      const coll = db.measurement
        .where('[metric_code+start_time]')
        .between([def.code, Dexie.minKey], [def.code, Dexie.maxKey])
        .filter((m) => !m.deleted_at);

      const count = await coll.count();
      if (count === 0) return null;

      const latest = await coll.last();

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
