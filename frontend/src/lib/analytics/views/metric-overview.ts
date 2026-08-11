import { getMetricStats } from '$lib/db/metric-stats';

export interface MetricOverview {
  metric_id: string;
  latest_value: string | null;
  latest_date: string | null;
  entry_count: number;
}

export async function fetchMetricOverview(): Promise<MetricOverview[]> {
  const stats = await getMetricStats();
  const overviews: MetricOverview[] = [];

  for (const [code, stat] of Object.entries(stats)) {
    if (stat.entry_count > 0) {
      overviews.push({
        metric_id: code,
        latest_value: stat.latest_value,
        latest_date: stat.latest_date,
        entry_count: stat.entry_count
      });
    }
  }

  return overviews;
}

export function overviewForMetric(
  overviews: MetricOverview[],
  metricId: string
): MetricOverview | null {
  return overviews.find((o) => o.metric_id === metricId) ?? null;
}
