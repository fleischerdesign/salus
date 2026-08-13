import { db } from '$lib/db/database';
import { MS_PER_DAY } from '$lib/utils/datetime';
import type {
  DashboardWidget,
  MetricDefinition,
  MetricWithPreference,
  Goal,
  Measurement
} from '$lib/db/types';
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

interface CachedMeta {
  timestamp: number;
  widgets: DashboardWidget[];
  metrics: MetricWithPreference[];
  goals: Goal[];
  metricById: Map<string, MetricWithPreference>;
}

let cachedMeta: CachedMeta | null = null;

export function invalidateDashboardMetaCache(): void {
  cachedMeta = null;
}

async function getDashboardMeta(): Promise<CachedMeta> {
  const now = Date.now();
  if (cachedMeta && now - cachedMeta.timestamp < 30000) {
    return cachedMeta;
  }

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
  const goals = allGoals.filter((g) => !g.deleted_at);
  const metricById = new Map(metrics.map((m) => [m.code, m]));

  cachedMeta = {
    timestamp: now,
    widgets,
    metrics,
    goals,
    metricById
  };

  return cachedMeta;
}

function getMetricLookbackDays(metricCode: string): number {
  switch (metricCode) {
    case 'weight':
    case 'body_fat':
    case 'blood_pressure':
    case 'systolic_bp':
    case 'diastolic_bp':
      return 7; // Low-frequency metrics with 7-day sparklines
    default:
      return 1; // High-frequency (heart_rate, steps, etc.) only need yesterday + today
  }
}

export async function fetchDashboard(date: string): Promise<DashboardData> {
  const dayStart = new Date(date + 'T00:00:00').getTime();
  const dayEnd = dayStart + MS_PER_DAY;
  const windowEnd = new Date(dayEnd).toISOString();

  const { widgets, metrics, goals, metricById } = await getDashboardMeta();

  if (widgets.length === 0) {
    return { widgets: [], metrics };
  }

  const activeMetricCodes: string[] = [
    ...new Set(
      widgets
        .filter((w) => w.widget_type === 'metric' && Boolean(w.metric_code))
        .map((w) => w.metric_code!)
    )
  ];

  // Cursor stream each metric directly without intermediate Dexie object cloning
  const measurementArrays = await Promise.all(
    activeMetricCodes.map(async (code) => {
      const lookback = getMetricLookbackDays(code);
      const metricWindowStart = new Date(dayStart - lookback * MS_PER_DAY).toISOString();
      const results: Measurement[] = [];

      await db.measurement
        .where('[metric_code+start_time]')
        .between([code, metricWindowStart], [code, windowEnd])
        .each((m) => {
          if (!m.deleted_at) {
            results.push(m);
          }
        });

      return results;
    })
  );

  const measurements = measurementArrays.flat();

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
      color: 'var(--color-primary-500)'
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
