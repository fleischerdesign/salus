import type { Measurement, Goal, MetricDefinition, DashboardWidget } from '../../db/types';
import { computeSparkline, deltaStr, yesterday, roundedSegments } from './helpers';

export interface WidgetViz {
  type:
    | 'number'
    | 'progress'
    | 'pills'
    | 'bar'
    | 'sparkline'
    | 'candlestick'
    | 'workout_launcher'
    | 'sleep_coach'
    | 'water_logger'
    | 'circadian_timeline';
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  color?: string;
  delta?: string | null;
  empty?: boolean;
  empty_text?: string;
  goal_label?: string;
  goal_percent?: number;
  goal_target?: number;
  sparkline_path?: string;
  segments?: Array<{ label: string; pct: number }>;
}

export interface VizContext {
  widget: DashboardWidget;
  metric: MetricDefinition;
  date: string;
  dayMeasurements: Measurement[];
  allMeasurements: Measurement[];
  goals: Goal[];
  color?: string;
}

export type BuilderFn = (ctx: VizContext) => WidgetViz;

function parseSleepJson(
  json: string | null
): { deep: number; rem: number; light: number; awake: number; total_seconds: number } | null {
  if (!json) return null;
  try {
    const d = JSON.parse(json);
    const stages = d.stages ?? d;
    const deep = (stages.deep_sleep_seconds ?? stages.deep ?? 0) as number;
    const rem = (stages.rem_sleep_seconds ?? stages.rem ?? 0) as number;
    const light = (stages.light_sleep_seconds ?? stages.light ?? 0) as number;
    const awake = (stages.awake_seconds ?? stages.awake ?? 0) as number;
    const total = deep + rem + light + awake;
    if (total <= 0) return null;
    return {
      deep: deep / 3600,
      rem: rem / 3600,
      light: light / 3600,
      awake: awake / 3600,
      total_seconds: total
    };
  } catch {
    return null;
  }
}

function stepsTrend(measurements: Measurement[], date: string): number | null {
  const dayM = measurements.filter((m) => m.start_time.startsWith(date) && !m.deleted_at);
  const counts = dayM.map((m) => m.value_numeric ?? 0);
  return counts.length > 0 ? Math.max(...counts) : null;
}

function latestWeight(measurements: Measurement[], date: string): number | null {
  const dayM = measurements
    .filter((m) => m.start_time.startsWith(date) && !m.deleted_at)
    .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
  return dayM[0]?.value_numeric ?? null;
}

function findGoal(goals: Goal[], sourceDataType: string, metricCode: string): Goal | null {
  return (
    goals.find((g) => g.deleted_at == null && g.is_active && g.metric_code === metricCode) ?? null
  );
}

/* ── Builders ── */

export function buildStepsViz(ctx: VizContext): WidgetViz {
  const todaySteps = stepsTrend(ctx.dayMeasurements, ctx.date);
  if (todaySteps == null) {
    return {
      type: 'progress',
      title: 'Steps',
      value: '—',
      unit: 'steps',
      empty: true,
      empty_text: 'No step data yet.'
    };
  }
  const yesterdaySteps = stepsTrend(ctx.allMeasurements, yesterday(ctx.date));
  const goal = findGoal(ctx.goals, 'steps', ctx.metric.code);
  const viz: WidgetViz = {
    type: 'progress',
    title: 'Steps',
    value: todaySteps.toLocaleString(),
    unit: 'steps',
    subtitle: 'today',
    color: ctx.color ?? '#4f46e5',
    delta: deltaStr(todaySteps, yesterdaySteps, { isInteger: true }),
    goal_target: goal ? goal.target_value : undefined,
    goal_percent: goal
      ? Math.min(100, Math.floor((todaySteps / goal.target_value) * 100))
      : undefined,
    goal_label: goal ? `Target: ${Math.round(goal.target_value).toLocaleString()} / day` : undefined
  };
  return viz;
}

export function buildHeartRateViz(ctx: VizContext): WidgetViz {
  const dayM = ctx.dayMeasurements.filter((m) => !m.deleted_at);
  if (dayM.length === 0) {
    return {
      type: 'pills',
      title: 'Heart Rate',
      value: '—',
      unit: 'bpm',
      empty: true,
      empty_text: 'No heart rate data.'
    };
  }
  const bpms = dayM.map((m) => m.value_numeric ?? 0).filter((v) => v > 0);
  if (bpms.length === 0) {
    return {
      type: 'pills',
      title: 'Heart Rate',
      value: '—',
      unit: 'bpm',
      empty: true,
      empty_text: 'No heart rate data.'
    };
  }
  const restingBpm = Math.round(Math.min(...bpms));
  const maxBpm = Math.round(Math.max(...bpms));
  const avgBpm = Math.round(bpms.reduce((s, v) => s + v, 0) / bpms.length);
  const yestM = ctx.allMeasurements.filter(
    (m) => m.start_time.startsWith(yesterday(ctx.date)) && !m.deleted_at
  );
  const yestBpms = yestM.map((m) => m.value_numeric ?? 0).filter((v) => v > 0);
  const yestResting = yestBpms.length > 0 ? Math.round(Math.min(...yestBpms)) : null;

  return {
    type: 'pills',
    title: 'Heart Rate',
    value: `${restingBpm}`,
    unit: 'bpm',
    color: ctx.color ?? '#4f46e5',
    subtitle: `Min ${restingBpm} · Max ${maxBpm} · Ø ${avgBpm}`,
    delta: deltaStr(restingBpm, yestResting, { unit: ' bpm', isInteger: true, upIsGood: false })
  };
}

export function buildSleepViz(ctx: VizContext): WidgetViz {
  const sleepM = ctx.dayMeasurements
    .filter((m) => !m.deleted_at && m.value_json)
    .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
  const latest = sleepM[0];
  const sleep = parseSleepJson(latest?.value_json ?? null);
  if (!sleep) {
    return {
      type: 'bar',
      title: 'Sleep',
      value: '—',
      unit: 'h',
      empty: true,
      empty_text: 'No sleep data yet.'
    };
  }
  const durationHours = sleep.total_seconds / 3600;
  const segments = roundedSegments([
    { label: 'Deep', value: sleep.deep * 3600 },
    { label: 'REM', value: sleep.rem * 3600 },
    { label: 'Light', value: sleep.light * 3600 },
    { label: 'Awake', value: sleep.awake * 3600 }
  ]);
  for (const seg of segments) {
    seg.label = `${seg.label}: ${seg.pct}%`;
  }
  return {
    type: 'bar',
    title: 'Sleep',
    value: durationHours.toFixed(1),
    unit: 'h',
    color: ctx.color ?? '#4f46e5',
    segments
  };
}

export function buildWeightViz(ctx: VizContext): WidgetViz {
  const w = latestWeight(ctx.dayMeasurements, ctx.date);
  if (w == null) {
    return {
      type: 'number',
      title: 'Weight',
      value: '—',
      unit: 'kg',
      empty: true,
      empty_text: 'No weight data yet.'
    };
  }
  const yestW = latestWeight(ctx.allMeasurements, yesterday(ctx.date));
  const recentWeights = ctx.allMeasurements
    .filter((m) => !m.deleted_at && m.value_numeric != null)
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    .slice(-7)
    .map((m) => m.value_numeric!);
  return {
    type: 'number',
    title: 'Weight',
    value: w.toFixed(1),
    unit: 'kg',
    color: ctx.color ?? '#4f46e5',
    delta: deltaStr(w, yestW, { unit: ' kg', upIsGood: false }),
    sparkline_path: computeSparkline(recentWeights)
  };
}

export function buildNutritionViz(ctx: VizContext): WidgetViz {
  const todayN = ctx.dayMeasurements.filter((m) => !m.deleted_at && m.value_json);
  if (todayN.length === 0) {
    return {
      type: 'bar',
      title: 'Nutrition',
      value: '—',
      unit: 'kcal',
      empty: true,
      empty_text: 'No nutrition data.'
    };
  }
  let proteinG = 0;
  let carbsG = 0;
  let fatG = 0;
  let totalKcal = 0;
  for (const m of todayN) {
    try {
      const d = JSON.parse(m.value_json!);
      proteinG += (d.protein_g ?? d.protein ?? 0) as number;
      carbsG += (d.carbs_g ?? d.carbs ?? 0) as number;
      fatG += (d.fat_g ?? d.fat ?? 0) as number;
      totalKcal += (d.total_kcal ?? d.calories ?? 0) as number;
    } catch {
      /* skip */
    }
  }
  if (totalKcal <= 0) {
    return {
      type: 'bar',
      title: 'Nutrition',
      value: '—',
      unit: 'kcal',
      empty: true,
      empty_text: 'No nutrition data.'
    };
  }
  const segments = roundedSegments([
    { label: `Protein: ${proteinG.toFixed(0)}g`, value: proteinG },
    { label: `Carbs: ${carbsG.toFixed(0)}g`, value: carbsG },
    { label: `Fat: ${fatG.toFixed(0)}g`, value: fatG }
  ]);
  return {
    type: 'bar',
    title: 'Nutrition',
    value: totalKcal.toFixed(0),
    unit: 'kcal',
    color: ctx.color ?? '#4f46e5',
    segments
  };
}

export function buildExerciseViz(ctx: VizContext): WidgetViz {
  const todayEx = ctx.dayMeasurements.filter((m) => !m.deleted_at && m.value_json);
  let totalMin = 0;
  for (const m of todayEx) {
    try {
      const d = JSON.parse(m.value_json!);
      totalMin += ((d.duration_seconds ?? d.duration ?? 0) as number) / 60;
    } catch {
      /* skip */
    }
  }
  if (totalMin <= 0) {
    return {
      type: 'number',
      title: 'Exercise',
      value: '—',
      unit: 'min',
      empty: true,
      empty_text: 'No exercise data.'
    };
  }
  return {
    type: 'number',
    title: 'Exercise',
    value: totalMin.toFixed(0),
    unit: 'min',
    color: ctx.color ?? '#4f46e5'
  };
}

export function buildGenericViz(ctx: VizContext): WidgetViz {
  const latestM = ctx.allMeasurements
    .filter(
      (m) => m.metric_code === ctx.metric.code && !m.deleted_at && m.start_time.startsWith(ctx.date)
    )
    .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())[0];

  if (!latestM) {
    return {
      type: 'number',
      title: ctx.metric.name || 'Metric',
      value: '—',
      color: ctx.color ?? '#4f46e5',
      empty: true,
      empty_text: 'No data recorded yet.'
    };
  }

  let value: string;
  if (latestM.value_numeric != null) {
    value =
      latestM.value_numeric % 1 === 0
        ? latestM.value_numeric.toFixed(0)
        : latestM.value_numeric.toFixed(1);
  } else if (latestM.value_text != null) {
    value = latestM.value_text;
  } else {
    value = '—';
  }

  const historyValues = ctx.allMeasurements
    .filter((m) => m.metric_code === ctx.metric.code && !m.deleted_at && m.value_numeric != null)
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    .slice(-7)
    .map((m) => m.value_numeric!);

  return {
    type: historyValues.length >= 2 ? 'sparkline' : 'number',
    title: ctx.metric.name || 'Metric',
    value,
    unit: ctx.metric.unit || undefined,
    color: ctx.color ?? '#4f46e5',
    sparkline_path: historyValues.length >= 2 ? computeSparkline(historyValues) : undefined,
    subtitle: latestM.start_time.split('T')[0]
  };
}

export const builders: Record<string, BuilderFn> = {
  steps: buildStepsViz,
  heart_rate: buildHeartRateViz,
  sleep: buildSleepViz,
  weight: buildWeightViz,
  nutrition: buildNutritionViz,
  exercise: buildExerciseViz
};

export function buildViz(ctx: VizContext): WidgetViz {
  const sdt = ctx.metric.source_data_type ?? 'generic';
  return (builders[sdt] ?? buildGenericViz)(ctx);
}
