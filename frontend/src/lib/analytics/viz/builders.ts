import type { Measurement, Goal, MetricDefinition, DashboardWidget } from '../../db/types';
import { computeSparkline, deltaStr, yesterday, roundedSegments } from './helpers';
import { MS_PER_DAY } from '$lib/utils/datetime';

export interface WidgetViz {
  type:
    | 'number'
    | 'pills'
    | 'bar'
    | 'sparkline'
    | 'candlestick'
    | 'workout_launcher'
    | 'sleep_coach'
    | 'water_logger'
    | 'circadian_timeline'
    | 'line_chart';
  title: string;
  value: string | number;
  unit?: string;
  subtitle?: string;
  color?: string;
  delta?: string | null;
  empty?: boolean;
  empty_text?: string;
  sparkline_path?: string;
  segments?: Array<{
    label: string;
    pct?: number;
    value?: number;
    unit?: string;
    color?: string;
    min?: number;
    max?: number;
    avg?: number;
    count?: number;
  }>;
  labels?: string[];
  series?: Array<{ label: string; data: number[]; color: string; yAxis?: string }>;
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

function stepsTrend(measurements: Measurement[]): number | null {
  const dayM = measurements.filter((m) => !m.deleted_at && m.value_numeric != null);
  if (dayM.length === 0) return null;
  const total = dayM.reduce((sum, m) => sum + (m.value_numeric ?? 0), 0);
  return total > 0 ? Math.round(total) : null;
}

function latestWeight(measurements: Measurement[]): number | null {
  const dayM = measurements
    .filter((m) => !m.deleted_at)
    .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
  return dayM[0]?.value_numeric ?? null;
}

/* ── Builders ── */

export function buildStepsViz(ctx: VizContext): WidgetViz {
  const dayM = ctx.dayMeasurements.filter((m) => m.metric_code === ctx.metric.code);
  const todaySteps = stepsTrend(dayM);
  if (todaySteps == null) {
    return {
      type: 'number',
      title: 'Steps',
      value: '—',
      unit: 'steps',
      empty: true,
      empty_text: 'No step data yet.'
    };
  }
  const yStart = new Date(yesterday(ctx.date) + 'T00:00:00').getTime();
  const yestM = ctx.allMeasurements.filter((m) => {
    if (m.metric_code !== ctx.metric.code) return false;
    const t = new Date(m.start_time).getTime();
    return t >= yStart && t < yStart + MS_PER_DAY && !m.deleted_at;
  });
  const yesterdaySteps = stepsTrend(yestM);
  return {
    type: 'number',
    title: 'Steps',
    value: todaySteps.toLocaleString(),
    unit: 'steps',
    color: ctx.color ?? '#4f46e5',
    delta: deltaStr(todaySteps, yesterdaySteps, { isInteger: true })
  };
}

export function buildHeartRateViz(ctx: VizContext): WidgetViz {
  const dayM = ctx.dayMeasurements.filter(
    (m) =>
      m.metric_code === ctx.metric.code &&
      !m.deleted_at &&
      m.value_numeric != null &&
      m.value_numeric > 0
  );
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
  const bpms = dayM.map((m) => m.value_numeric!);
  const dayMin = Math.round(Math.min(...bpms));
  const dayMax = Math.round(Math.max(...bpms));
  const dayAvg = Math.round(bpms.reduce((s, v) => s + v, 0) / bpms.length);

  // Latest measurement on that day
  const sortedDay = [...dayM].sort(
    (a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime()
  );
  const latestBpm = Math.round(sortedDay[0].value_numeric!);

  // Yesterday delta
  const yStart = new Date(yesterday(ctx.date) + 'T00:00:00').getTime();
  const yestM = ctx.allMeasurements.filter((m) => {
    if (m.metric_code !== ctx.metric.code) return false;
    const t = new Date(m.start_time).getTime();
    return (
      t >= yStart &&
      t < yStart + MS_PER_DAY &&
      !m.deleted_at &&
      m.value_numeric != null &&
      m.value_numeric > 0
    );
  });
  const yestBpms = yestM.map((m) => m.value_numeric!);
  const yestMin = yestBpms.length > 0 ? Math.round(Math.min(...yestBpms)) : null;

  // 24 Hourly Buckets (0..23) for Apple Health style Range Pills in single O(N) pass
  const hourlyVals: number[][] = Array.from({ length: 24 }, () => []);
  for (const m of dayM) {
    if (m.value_numeric != null && m.value_numeric > 0) {
      const h = new Date(m.start_time).getHours();
      if (h >= 0 && h < 24) {
        hourlyVals[h].push(m.value_numeric);
      }
    }
  }

  const buckets = hourlyVals.map((vals, h) => {
    if (vals.length === 0) {
      return {
        label: `${h.toString().padStart(2, '0')}:00`,
        min: 0,
        max: 0,
        avg: 0,
        count: 0
      };
    }
    return {
      label: `${h.toString().padStart(2, '0')}:00`,
      min: Math.round(Math.min(...vals)),
      max: Math.round(Math.max(...vals)),
      avg: Math.round(vals.reduce((s, v) => s + v, 0) / vals.length),
      count: vals.length
    };
  });

  return {
    type: 'pills',
    title: 'Heart Rate',
    value: latestBpm,
    unit: 'bpm',
    color: ctx.color ?? '#f43f5e',
    subtitle: `${dayMin}–${dayMax} bpm (Ø ${dayAvg})`,
    delta: deltaStr(dayMin, yestMin, { unit: ' bpm', isInteger: true, upIsGood: false }),
    segments: buckets.map((b) => ({
      label: b.label,
      value: b.max,
      min: b.min,
      max: b.max,
      avg: b.avg,
      count: b.count
    }))
  };
}

export function buildSleepViz(ctx: VizContext): WidgetViz {
  const sleepM = ctx.dayMeasurements
    .filter((m) => m.metric_code === ctx.metric.code && !m.deleted_at && m.value_json)
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
  const dayM = ctx.dayMeasurements.filter((m) => m.metric_code === ctx.metric.code);
  const w = latestWeight(dayM);
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
  const yStart = new Date(yesterday(ctx.date) + 'T00:00:00').getTime();
  const yestM = ctx.allMeasurements.filter((m) => {
    if (m.metric_code !== ctx.metric.code) return false;
    const t = new Date(m.start_time).getTime();
    return t >= yStart && t < yStart + MS_PER_DAY && !m.deleted_at;
  });
  const yestW = latestWeight(yestM);
  const recentWeights = ctx.allMeasurements
    .filter((m) => m.metric_code === ctx.metric.code && !m.deleted_at && m.value_numeric != null)
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
      proteinG += (d.protein_grams ?? d.protein_g ?? d.protein ?? 0) as number;
      carbsG += (d.carbs_grams ?? d.carbs_g ?? d.carbs ?? 0) as number;
      fatG += (d.fat_grams ?? d.fat_g ?? d.fat ?? 0) as number;
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
  const latestM = ctx.dayMeasurements
    .filter((m) => m.metric_code === ctx.metric.code && !m.deleted_at)
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

export function buildBloodPressureViz(ctx: VizContext): WidgetViz {
  const sysM = ctx.allMeasurements
    .filter((m) => m.metric_code === 'systolic_bp' && !m.deleted_at && m.value_numeric != null)
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());
  const diaM = ctx.allMeasurements
    .filter((m) => m.metric_code === 'diastolic_bp' && !m.deleted_at && m.value_numeric != null)
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime());

  if (sysM.length === 0 || diaM.length === 0) {
    return {
      type: 'line_chart',
      title: 'Blood Pressure',
      value: '—',
      unit: 'mmHg',
      color: ctx.color ?? '#ef4444',
      empty: true,
      empty_text: 'No blood pressure data.'
    };
  }

  const byDate = new Map<string, { systolic: number[]; diastolic: number[] }>();
  for (const m of sysM) {
    const d = m.start_time.split('T')[0];
    if (!byDate.has(d)) byDate.set(d, { systolic: [], diastolic: [] });
    byDate.get(d)!.systolic.push(m.value_numeric!);
  }
  for (const m of diaM) {
    const d = m.start_time.split('T')[0];
    if (!byDate.has(d)) byDate.set(d, { systolic: [], diastolic: [] });
    byDate.get(d)!.diastolic.push(m.value_numeric!);
  }

  const sorted = [...byDate.entries()]
    .filter(([, v]) => v.systolic.length > 0 && v.diastolic.length > 0)
    .sort(([a], [b]) => a.localeCompare(b));

  if (sorted.length === 0) {
    return {
      type: 'line_chart',
      title: 'Blood Pressure',
      value: '—',
      unit: 'mmHg',
      color: ctx.color ?? '#ef4444',
      empty: true,
      empty_text: 'No blood pressure data.'
    };
  }

  const recent = sorted.slice(-14);
  const labels = recent.map(([d]) => d.slice(5));
  const systolicData = recent.map(([, v]) => {
    const avg = v.systolic.reduce((s, x) => s + x, 0) / v.systolic.length;
    return Math.round(avg * 10) / 10;
  });
  const diastolicData = recent.map(([, v]) => {
    const avg = v.diastolic.reduce((s, x) => s + x, 0) / v.diastolic.length;
    return Math.round(avg * 10) / 10;
  });

  const latestSys = systolicData[systolicData.length - 1];
  const latestDia = diastolicData[diastolicData.length - 1];

  return {
    type: 'line_chart',
    title: 'Blood Pressure',
    value: `${latestSys.toFixed(0)} / ${latestDia.toFixed(0)}`,
    unit: 'mmHg',
    color: ctx.color ?? '#ef4444',
    labels,
    series: [
      { label: 'Systolic', data: systolicData, color: '#ef4444' },
      { label: 'Diastolic', data: diastolicData, color: '#3b82f6' }
    ]
  };
}

export const builders: Record<string, BuilderFn> = {
  steps: buildStepsViz,
  heart_rate: buildHeartRateViz,
  sleep: buildSleepViz,
  weight: buildWeightViz,
  nutrition: buildNutritionViz,
  exercise: buildExerciseViz,
  blood_pressure: buildBloodPressureViz
};

export function buildViz(ctx: VizContext): WidgetViz {
  const sdt = ctx.metric.source_data_type ?? 'generic';
  return (builders[sdt] ?? buildGenericViz)(ctx);
}
