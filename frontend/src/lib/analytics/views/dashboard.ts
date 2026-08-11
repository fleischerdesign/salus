import Dexie from 'dexie';
import { db } from '$lib/db/database';
import type { DashboardWidget, MetricDefinition, MetricWithPreference } from '$lib/db/types';
import { mergeMetricPrefs } from '$lib/db/types';
import { buildViz, type WidgetViz } from '../viz/builders';

export interface DashboardWidgetView {
  id: string;
  widget_type: string;
  metric_code: string;
  size: string;
  position: number;
  viz: WidgetViz;
}

export interface DashboardData {
  widgets: DashboardWidgetView[];
  metrics: MetricWithPreference[];
}

export async function fetchDashboard(date: string): Promise<DashboardData> {
  const dayStart = new Date(date + 'T00:00:00').getTime();
  const dayEnd = dayStart + 86400000;
  const windowStart = new Date(dayStart - 30 * 86400000).toISOString();

  const [allWidgets, allMetrics, allPrefs, allGoals] = await Promise.all([
    db.dashboard_widget.toArray(),
    db.metric_definition.toArray(),
    db.user_metric_preference.toArray(),
    db.goal.toArray()
  ]);

  const widgets = (allWidgets as DashboardWidget[])
    .filter((w) => !w.deleted_at && w.is_visible)
    .sort((a, b) => a.position - b.position);
  const metrics = mergeMetricPrefs(allMetrics as MetricDefinition[], allPrefs);

  if (widgets.length === 0) {
    return { widgets: [], metrics };
  }

  const goals = allGoals.filter((g) => !g.deleted_at);
  const metricById = new Map(metrics.map((m) => [m.code, m]));

  const activeMetricCodes = [
    ...new Set(
      widgets
        .filter((w) => w.widget_type === 'metric' && Boolean(w.metric_code))
        .map((w) => w.metric_code)
    )
  ];

  const measurementArrays = await Promise.all(
    activeMetricCodes.map((code) =>
      db.measurement
        .where('[metric_code+start_time]')
        .between([code, windowStart], [code, Dexie.maxKey])
        .toArray()
    )
  );

  const measurements = measurementArrays.flat().filter((m) => !m.deleted_at);

  const dayMeasurements = measurements.filter((m) => {
    const t = new Date(m.start_time).getTime();
    return t >= dayStart && t < dayEnd;
  });

  const widgetViews: DashboardWidgetView[] = widgets.map((w) => {
    if (w.widget_type !== 'metric' || !w.metric_code) {
      return {
        id: w.id,
        widget_type: w.widget_type,
        metric_code: '',
        size: w.size,
        position: w.position,
        viz: {
          type: w.widget_type as WidgetViz['type'],
          title:
            w.widget_type === 'workout_launcher'
              ? 'Workout Launcher'
              : w.widget_type === 'sleep_coach'
                ? 'Sleep Coach'
                : w.widget_type === 'water_logger'
                  ? 'Water Intake'
                  : 'Circadian Timeline',
          value: ''
        }
      };
    }

    const metric = metricById.get(w.metric_code);
    if (!metric) {
      return {
        id: w.id,
        widget_type: 'metric',
        metric_code: w.metric_code,
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
      goals,
      color: '#4f46e5'
    });

    return {
      id: w.id,
      widget_type: 'metric',
      metric_code: w.metric_code,
      size: w.size,
      position: w.position,
      viz
    };
  });

  return { widgets: widgetViews, metrics };
}
