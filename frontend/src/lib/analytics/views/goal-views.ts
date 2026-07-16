import { db } from '$lib/db/database';
import type { Goal, Measurement } from '$lib/db/types';
import { mergeMetricPrefs } from '$lib/db/types';
import { computeGoalProgress } from '$lib/analytics/calculations';
import type { GoalStatus } from '$lib/analytics/calculations';
import { linearRegression, predictionInterval } from '$lib/analytics/stats';

export interface GoalView {
  id: string;
  metric_name: string;
  metric_color: string;
  metric_icon: string;
  metric_unit: string;
  target_value: number;
  direction: string;
  frequency: string;
  deadline: string | null;
  is_active: boolean;
  progress: {
    current_value: number | null;
    target_value: number;
    percent: number;
    status: GoalStatus;
    is_fulfilled: boolean;
  };
  forecast?: {
    on_track: boolean;
    predicted: number;
    ci_lower: number;
    ci_upper: number;
    r_squared: number;
  } | null;
}

interface ForecastResult {
  on_track: boolean;
  predicted: number;
  ci_lower: number;
  ci_upper: number;
  r_squared: number;
}

function computeDeadlineForecast(
  goal: Goal,
  measurements: Measurement[],
  createdAtStr: string
): ForecastResult | null {
  const relevant = measurements
    .filter((m) => m.metric_code === goal.metric_code && !m.deleted_at)
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());

  if (relevant.length < 3) return null;

  const createdDate = new Date(createdAtStr);
  const xs: number[] = [];
  const ys: number[] = [];

  for (const m of relevant) {
    if (m.value_numeric == null) continue;
    const mDate = new Date(m.start_time);
    const daysSince = Math.floor((mDate.getTime() - createdDate.getTime()) / (1000 * 60 * 60 * 24));
    xs.push(daysSince);
    ys.push(m.value_numeric);
  }

  if (ys.length < 3) return null;

  const reg = linearRegression(xs, ys);
  if (!reg) return null;

  if (!goal.deadline) return null;
  const deadlineDate = new Date(goal.deadline);
  const daysTotal = Math.floor(
    (deadlineDate.getTime() - createdDate.getTime()) / (1000 * 60 * 60 * 24)
  );

  const pi = predictionInterval(reg, daysTotal, 0.8);
  if (!pi) return null;

  const onTrack =
    goal.direction === 'increase' ? pi.lower >= goal.target_value : pi.upper <= goal.target_value;

  return {
    on_track: onTrack,
    predicted: Math.round(pi.point_estimate * 100) / 100,
    ci_lower: Math.round(pi.lower * 100) / 100,
    ci_upper: Math.round(pi.upper * 100) / 100,
    r_squared: Math.round(reg.r_squared * 10000) / 10000
  };
}

export async function fetchGoalViews(): Promise<GoalView[]> {
  const goals = await db.goal.toArray();
  const metricDefs = await db.metric_definition.toArray();
  const prefs = await db.user_metric_preference.toArray();
  const measurements = await db.measurement.toArray();

  const metrics = mergeMetricPrefs(metricDefs, prefs);
  const metricById = new Map(metrics.map((m) => [m.code, m]));

  return goals
    .filter((g) => !g.deleted_at)
    .map((g) => {
      const metric = metricById.get(g.metric_code);
      const currentValue = computeGoalCurrent(measurements, g.metric_code, g.frequency);

      const deadlinePassed = g.deadline != null ? new Date(g.deadline) < new Date() : false;
      const progress = computeGoalProgress(
        currentValue,
        g.target_value,
        g.direction as 'INCREASE' | 'DECREASE',
        g.frequency as 'DAILY' | 'WEEKLY' | 'ONCE',
        deadlinePassed
      );

      let forecastVal = null;
      if (g.frequency === 'once' && g.deadline && !deadlinePassed) {
        forecastVal = computeDeadlineForecast(g, measurements, g.created_at);
      }

      return {
        id: g.id,
        metric_name: metric?.name ?? 'Unknown',
        metric_color: metric?.color ?? '#4f46e5',
        metric_icon: metric?.icon ?? 'track-changes',
        metric_unit: metric?.unit ?? '',
        target_value: g.target_value,
        direction: g.direction,
        frequency: g.frequency,
        deadline: g.deadline,
        is_active: g.is_active,
        progress: {
          current_value: currentValue,
          target_value: g.target_value,
          percent: progress.percent,
          status: progress.status,
          is_fulfilled: progress.isFulfilled
        },
        forecast: forecastVal
      };
    });
}

export async function fetchGoalView(goalId: string): Promise<GoalView | null> {
  const g = await db.goal.get(goalId);
  if (!g || g.deleted_at) return null;
  const metricDef = await db.metric_definition.get(g.metric_code);
  const pref = await db.user_metric_preference.where('metric_code').equals(g.metric_code).first();
  const metric = metricDef
    ? {
        ...metricDef,
        color: pref?.color ?? '#4f46e5',
        icon: pref?.icon ?? 'track-changes',
        widget_size: pref?.widget_size ?? 'medium',
        widget_enabled: pref?.widget_enabled ?? false,
        enabled: pref?.enabled ?? true,
        position: pref?.position ?? 0
      }
    : undefined;
  const measurements = await db.measurement.where('metric_code').equals(g.metric_code).toArray();
  const currentValue = computeGoalCurrent(measurements, g.metric_code, g.frequency);

  const deadlinePassed = g.deadline != null ? new Date(g.deadline) < new Date() : false;
  const progress = computeGoalProgress(
    currentValue,
    g.target_value,
    g.direction as 'INCREASE' | 'DECREASE',
    g.frequency as 'DAILY' | 'WEEKLY' | 'ONCE',
    deadlinePassed
  );

  let forecastVal = null;
  if (g.frequency === 'once' && g.deadline && !deadlinePassed) {
    forecastVal = computeDeadlineForecast(g, measurements, g.created_at);
  }

  return {
    id: g.id,
    metric_name: metric?.name ?? 'Unknown',
    metric_color: metric?.color ?? '#4f46e5',
    metric_icon: metric?.icon ?? 'track-changes',
    metric_unit: metric?.unit ?? '',
    target_value: g.target_value,
    direction: g.direction,
    frequency: g.frequency,
    deadline: g.deadline,
    is_active: g.is_active,
    progress: {
      current_value: currentValue,
      target_value: g.target_value,
      percent: progress.percent,
      status: progress.status,
      is_fulfilled: progress.isFulfilled
    },
    forecast: forecastVal
  };
}

function computeGoalCurrent(
  measurements: Measurement[],
  metricCode: string,
  frequency: string
): number | null {
  const relevant = measurements.filter((m) => m.metric_code === metricCode && !m.deleted_at);

  if (relevant.length === 0) return null;

  const now = new Date();
  let filtered = relevant.filter((m) => {
    const t = new Date(m.start_time);
    if (frequency === 'DAILY') {
      return t.toDateString() === now.toDateString();
    }
    if (frequency === 'WEEKLY') {
      const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      return t >= weekAgo;
    }
    return true;
  });

  if (filtered.length === 0) {
    filtered = relevant;
  }

  const values = filtered.map((m) => m.value_numeric).filter((v): v is number => v != null);

  if (values.length === 0) return null;

  if (frequency === 'DAILY' || frequency === 'ONCE') {
    return Math.max(...values);
  }
  return values.reduce((a, b) => a + b, 0) / values.length;
}
