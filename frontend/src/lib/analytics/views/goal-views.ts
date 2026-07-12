import { db } from '$lib/db/database';
import type { Goal, Measurement, MetricType } from '$lib/db/types';
import { computeGoalProgress } from '$lib/analytics/calculations';
import type { GoalStatus } from '$lib/analytics/calculations';

export interface GoalView {
  id: number;
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
}

export async function fetchGoalViews(): Promise<GoalView[]> {
  const goals = await db.goal.toArray();
  const metrics = await db.metric_type.toArray();
  const measurements = await db.measurement.toArray();

  const metricById = new Map(metrics.map((m) => [m.id, m]));

  return goals
    .filter((g) => !g.deleted_at)
    .map((g) => {
      const metric = metricById.get(g.metric_type_id);
      const currentValue = computeGoalCurrent(
        measurements,
        g.metric_type_id,
        g.frequency,
      );

      const deadlinePassed =
        g.deadline != null ? new Date(g.deadline) < new Date() : false;
      const progress = computeGoalProgress(
        currentValue,
        g.target_value,
        g.direction as 'INCREASE' | 'DECREASE',
        g.frequency as 'DAILY' | 'WEEKLY' | 'ONCE',
        deadlinePassed,
      );

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
          is_fulfilled: progress.isFulfilled,
        },
      };
    });
}

function computeGoalCurrent(
  measurements: Measurement[],
  metricTypeId: number,
  frequency: string,
): number | null {
  const relevant = measurements.filter(
    (m) => m.metric_type_id === metricTypeId && !m.deleted_at,
  );

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

  const values = filtered
    .map((m) => m.value_numeric)
    .filter((v): v is number => v != null);

  if (values.length === 0) return null;

  if (frequency === 'DAILY' || frequency === 'ONCE') {
    return Math.max(...values);
  }
  return values.reduce((a, b) => a + b, 0) / values.length;
}
