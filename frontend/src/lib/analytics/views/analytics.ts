import { db } from '$lib/db/database';
import type { Measurement } from '$lib/db/types';
import { calcBmrCunningham, calcTef, calcTdee, mapSleepStage, mapExerciseType } from '../calculations';

const RANGE_DAYS: Record<string, number> = { '7d': 7, '30d': 30, '90d': 90, '1y': 365 };

interface AnalyticsResult {
  steps_labels: string[];
  steps_data: number[];
  weight_labels: string[];
  weight_data: number[];
  sleep_list: Array<{
    date: string;
    duration_hours: number;
    awake_pct: number;
    light_pct: number;
    deep_pct: number;
    rem_pct: number;
  }>;
  latest_sleep: {
    date: string;
    duration_hours: number;
    awake_pct: number;
    light_pct: number;
    deep_pct: number;
    rem_pct: number;
  } | null;
  weight_trend: {
    points: Array<{ date: string; weight_kg: number }>;
    current: number | null;
    start: number | null;
    delta: number | null;
  };
  tdee: {
    tdee_kcal: number;
    bmr_kcal: number;
    pal_factor: number;
    hrr_pct: number;
  } | null;
  exercise_sessions: Array<{
    type_name: string;
    date: string;
    time: string;
    duration_seconds: number;
    distance_meters: number;
    calories: number;
  }>;
  days: number;
}

export async function fetchAnalytics(rangeKey: string = '30d'): Promise<AnalyticsResult> {
  const days = RANGE_DAYS[rangeKey] ?? 30;
  const allMeasurements = await db.measurement.toArray();
  const measurements = allMeasurements.filter((m) => !m.deleted_at);
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);

  const recent = measurements.filter((m) => new Date(m.start_time) >= cutoff);

  const stepsTrend = computeStepsTrend(recent, days);
  const weightTrend = computeWeightTrend(recent, days);
  const sleepList = computeSleepList(recent, days);
  const tdee = computeTdee(weightTrend, recent);
  const exerciseSessions = computeExerciseHistory(recent, days);

  return {
    steps_labels: stepsTrend.map((s) => s.date),
    steps_data: stepsTrend.map((s) => s.count),
    weight_labels: weightTrend.map((w) => w.date),
    weight_data: weightTrend.map((w) => Math.round(w.weight_kg * 10) / 10),
    sleep_list: sleepList,
    latest_sleep: sleepList.length > 0 ? sleepList[sleepList.length - 1] : null,
    weight_trend: {
      points: weightTrend.map((w) => ({ date: w.date, weight_kg: Math.round(w.weight_kg * 10) / 10 })),
      current: weightTrend.length > 0 ? weightTrend[weightTrend.length - 1].weight_kg : null,
      start: weightTrend.length > 0 ? weightTrend[0].weight_kg : null,
      delta: weightTrend.length >= 2 ? Math.round((weightTrend[weightTrend.length - 1].weight_kg - weightTrend[0].weight_kg) * 10) / 10 : null,
    },
    tdee,
    exercise_sessions: exerciseSessions,
    days,
  };
}

interface StepDay { date: string; count: number }
function computeStepsTrend(measurements: Measurement[], days: number): StepDay[] {
  const stepMeasurements = measurements.filter(
    (m) => m.data_type === 'number',
  );
  const byDate = new Map<string, number[]>();
  for (const m of stepMeasurements) {
    if (m.value_numeric == null) continue;
    const date = m.start_time.slice(0, 10);
    const arr = byDate.get(date) ?? [];
    arr.push(m.value_numeric);
    byDate.set(date, arr);
  }
  return [...byDate.entries()]
    .map(([date, counts]) => ({ date: date.slice(5), count: Math.max(...counts) }))
    .sort((a, b) => a.date.localeCompare(b.date));
}

interface WeightPoint { date: string; weight_kg: number }
function computeWeightTrend(measurements: Measurement[], days: number): WeightPoint[] {
  const weightM = measurements.filter(
    (m) => m.data_type === 'number' && m.value_numeric != null,
  );
  const seen = new Set<string>();
  const points: WeightPoint[] = [];
  for (const m of weightM.sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())) {
    const date = m.start_time.slice(0, 5);
    if (seen.has(date)) continue;
    seen.add(date);
    points.push({ date: m.start_time.slice(0, 10), weight_kg: m.value_numeric! });
  }
  return points.reverse();
}

function computeSleepList(measurements: Measurement[], _days: number) {
  const sleepM = measurements.filter((m) => m.value_json);
  const results: Array<{
    date: string;
    duration_hours: number;
    awake_pct: number;
    light_pct: number;
    deep_pct: number;
    rem_pct: number;
  }> = [];
  for (const m of sleepM) {
    try {
      const d = JSON.parse(m.value_json!);
      const stages = d.stages ?? d;
      const deep = (stages.deep_sleep_seconds ?? stages.deep ?? 0) as number;
      const rem = (stages.rem_sleep_seconds ?? stages.rem ?? 0) as number;
      const light = (stages.light_sleep_seconds ?? stages.light ?? 0) as number;
      const awake = (stages.awake_seconds ?? stages.awake ?? 0) as number;
      const total = deep + rem + light + awake;
      if (total <= 0) continue;
      results.push({
        date: m.start_time.slice(0, 10),
        duration_hours: Math.round((total / 3600) * 100) / 100,
        awake_pct: Math.round((awake / total) * 1000) / 10,
        light_pct: Math.round((light / total) * 1000) / 10,
        deep_pct: Math.round((deep / total) * 1000) / 10,
        rem_pct: Math.round((rem / total) * 1000) / 10,
      });
    } catch { /* skip */ }
  }
  return results.sort((a, b) => a.date.localeCompare(b.date));
}

function computeTdee(
  weightTrend: WeightPoint[],
  measurements: Measurement[],
): AnalyticsResult['tdee'] {
  if (weightTrend.length === 0) return null;
  const current = weightTrend[weightTrend.length - 1].weight_kg;
  const bmr = calcBmrCunningham(current);
  const hrMeasurements = measurements.filter((m) => m.value_numeric != null && m.value_numeric > 0);
  const hrResting = Math.min(...(hrMeasurements.map((m) => m.value_numeric!).length > 0 ? hrMeasurements.map((m) => m.value_numeric!) : [60]));
  const hrAvg = hrMeasurements.map((m) => m.value_numeric!).reduce((a, b) => a + b, 0) / (hrMeasurements.length || 1);
  const tdeeResult = calcTdee(bmr, hrAvg || 75, hrResting || 60);
  if (!tdeeResult) return null;
  return {
    tdee_kcal: tdeeResult.tdeeKcal,
    bmr_kcal: Math.round(bmr * 10) / 10,
    pal_factor: tdeeResult.palFactor,
    hrr_pct: tdeeResult.hrrPct,
  };
}

function computeExerciseHistory(measurements: Measurement[], _days: number) {
  const exMeasurements = measurements.filter((m) => m.value_json);
  const sessions: AnalyticsResult['exercise_sessions'] = [];
  for (const m of exMeasurements) {
    try {
      const d = JSON.parse(m.value_json!);
      const typeCode = (d.exercise_type ?? d.type) as number | undefined;
      sessions.push({
        type_name: typeCode != null ? mapExerciseType(typeCode) : 'Exercise',
        date: m.start_time.slice(0, 10),
        time: m.start_time.slice(11, 19),
        duration_seconds: (d.duration_seconds ?? d.duration ?? 0) as number,
        distance_meters: (d.distance_meters ?? d.distance ?? 0) as number,
        calories: (d.calories ?? 0) as number,
      });
    } catch { /* skip */ }
  }
  return sessions.slice(0, 5);
}
