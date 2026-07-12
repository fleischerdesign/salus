import { db } from '$lib/db/database';
import type { DashboardWidget, Measurement, MetricType, Goal } from '$lib/db/types';
import { buildViz, type WidgetViz } from '../viz/builders';

export interface DashboardWidgetView {
  id: number;
  metric_type_id: number;
  size: string;
  position: number;
  viz: WidgetViz;
}

export interface DashboardData {
  widgets: DashboardWidgetView[];
  metrics: MetricType[];
}

export async function fetchDashboard(date: string): Promise<DashboardData> {
  const [allWidgets, allMetrics, allMeasurements, allGoals] = await Promise.all([
    db.dashboard_widget.toArray(),
    db.metric_type.toArray(),
    db.measurement.toArray(),
    db.goal.toArray()
  ]);

  const widgets = (allWidgets as DashboardWidget[])
    .filter((w) => !w.deleted_at && w.is_visible)
    .sort((a, b) => a.position - b.position);

  const metrics = allMetrics.filter((m) => !m.deleted_at);
  const measurements = allMeasurements.filter((m) => !m.deleted_at);
  const goals = allGoals.filter((g) => !g.deleted_at);
  const metricById = new Map(metrics.map((m) => [m.id, m]));

  const dayStart = new Date(date + 'T00:00:00').getTime();
  const dayEnd = dayStart + 86400000;
  const dayMeasurements = measurements.filter((m) => {
    const t = new Date(m.start_time).getTime();
    return t >= dayStart && t < dayEnd;
  });

  const widgetViews: DashboardWidgetView[] = widgets.map((w) => {
    const metric = metricById.get(w.metric_type_id);
    if (!metric) {
      return {
        id: w.id,
        metric_type_id: w.metric_type_id,
        size: w.size,
        position: w.position,
        viz: {
          type: 'number',
          title: 'Unknown',
          value: '—',
          empty: true,
          empty_text: 'Metric not found'
        }
      };
    }

    const viz = buildViz({
      widget: w,
      metric,
      date,
      dayMeasurements,
      allMeasurements: measurements,
      goals
    });

    return {
      id: w.id,
      metric_type_id: w.metric_type_id,
      size: w.size,
      position: w.position,
      viz
    };
  });

  return { widgets: widgetViews, metrics };
}
