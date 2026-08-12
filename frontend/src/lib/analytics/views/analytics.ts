import Dexie, { liveQuery } from 'dexie';
import { db } from '$lib/db/database';
import type { Measurement } from '$lib/db/types';
import {
  benjaminiHochberg,
  bmrCunningham,
  bmrMifflinStJeor,
  hrrPct,
  hrMaxTanaka,
  linearRegression,
  palFromHrr,
  pearson,
  spearman,
  predictionInterval,
  recoveryComposite,
  sleepDebtCumulative,
  tdee
} from '$lib/analytics/stats';

interface Correlation {
  metric_a: string;
  metric_b: string;
  pearson_r: number;
  pearson_p: number;
  p_adjusted_bh: number;
  effect_size_d: number;
  ci_lower: number;
  ci_upper: number;
  n: number;
  interpretation: string;
}

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

const RANGE_DAYS: Record<string, number> = { '7d': 7, '30d': 30, '90d': 90, '1y': 365 };

function computeAnalytics(measurements: Measurement[], rangeKey: string): AnalyticsResult {
  const days = RANGE_DAYS[rangeKey] ?? 30;
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - days);
  const recent = measurements.filter((m) => new Date(m.start_time) >= cutoff && !m.deleted_at);

  const stepsTrend = computeSteps(recent);
  const weightTrend = computeWeight(recent);
  const sleepList = computeSleep(recent);
  const tdeeResult = computeTdee(weightTrend, recent);
  const exerciseSessions = computeExercise(recent);
  const latestSleep = sleepList.length > 0 ? sleepList[sleepList.length - 1] : null;

  return {
    steps_labels: stepsTrend.map((s) => s.date),
    steps_data: stepsTrend.map((s) => s.count),
    weight_labels: weightTrend.map((w) => w.date),
    weight_data: weightTrend.map((w) => Math.round(w.weight_kg * 10) / 10),
    sleep_list: sleepList,
    latest_sleep: latestSleep
      ? {
          date: latestSleep.date,
          duration_hours: latestSleep.duration_hours,
          awake_pct: latestSleep.awake_pct,
          light_pct: latestSleep.light_pct,
          deep_pct: latestSleep.deep_pct,
          rem_pct: latestSleep.rem_pct
        }
      : null,
    weight_trend: {
      points: weightTrend.map((w) => ({
        date: w.date,
        weight_kg: Math.round(w.weight_kg * 10) / 10
      })),
      current: weightTrend.length > 0 ? weightTrend[weightTrend.length - 1].weight_kg : null,
      start: weightTrend.length > 0 ? weightTrend[0].weight_kg : null,
      delta:
        weightTrend.length >= 2
          ? Math.round(
              (weightTrend[weightTrend.length - 1].weight_kg - weightTrend[0].weight_kg) * 10
            ) / 10
          : null
    },
    tdee: tdeeResult,
    exercise_sessions: exerciseSessions,
    days
  };
}

interface StepDay {
  date: string;
  count: number;
}

function computeSteps(measurements: Measurement[]): StepDay[] {
  const stepM = measurements.filter(
    (m) => (m.data_type === 'steps' || m.metric_code === 'steps') && m.value_numeric != null
  );
  const byDate = new Map<string, number[]>();
  for (const m of stepM) {
    const date = m.start_time.slice(0, 10);
    const arr = byDate.get(date) ?? [];
    arr.push(m.value_numeric!);
    byDate.set(date, arr);
  }
  return [...byDate.entries()]
    .map(([date, counts]) => ({
      date: date.slice(5),
      count: Math.max(...counts)
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
}

interface WeightPoint {
  date: string;
  weight_kg: number;
}

function computeWeight(measurements: Measurement[]): WeightPoint[] {
  const weightM = measurements.filter(
    (m) => (m.data_type === 'weight' || m.metric_code === 'weight') && m.value_numeric != null
  );
  const seen = new Set<string>();
  const points: WeightPoint[] = [];
  for (const m of weightM.sort(
    (a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime()
  )) {
    const date = m.start_time.slice(0, 10);
    if (seen.has(date)) continue;
    seen.add(date);
    points.push({ date, weight_kg: m.value_numeric! });
  }
  return points.reverse();
}

function computeSleep(measurements: Measurement[]): Array<{
  date: string;
  duration_hours: number;
  awake_pct: number;
  light_pct: number;
  deep_pct: number;
  rem_pct: number;
}> {
  const sleepM = measurements.filter((m) => m.data_type === 'sleep' || m.metric_code === 'sleep');
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
      if (!m.value_json) continue;
      const d = JSON.parse(m.value_json);
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
        rem_pct: Math.round((rem / total) * 1000) / 10
      });
    } catch {
      /* skip malformed JSON */
    }
  }
  return results.sort((a, b) => a.date.localeCompare(b.date));
}

function computeTdee(
  weightTrend: WeightPoint[],
  measurements: Measurement[]
): AnalyticsResult['tdee'] {
  if (weightTrend.length === 0) return null;
  const current = weightTrend[weightTrend.length - 1].weight_kg;
  let bmr = bmrCunningham(current, null);
  if (bmr === null) {
    bmr = bmrMifflinStJeor(current, getUserHeight(), 30, null);
  }
  const hrM = measurements.filter(
    (m) => m.data_type === 'heart_rate' && m.value_numeric != null && m.value_numeric > 0
  );
  const hrValues = hrM.map((m) => m.value_numeric!);
  const hrResting = hrValues.length > 0 ? Math.min(...hrValues) : 60;
  const hrAvg = hrValues.length > 0 ? hrValues.reduce((a, b) => a + b, 0) / hrValues.length : 75;
  const hrMax = hrMaxTanaka(30);
  const hrrPctVal = hrrPct(hrAvg, hrResting, hrMax);
  const pal = palFromHrr(hrrPctVal);
  const tdeeVal = tdee(bmr, pal, 0);
  return {
    tdee_kcal: tdeeVal,
    bmr_kcal: Math.round(bmr * 10) / 10,
    pal_factor: Math.round(pal * 100) / 100,
    hrr_pct: Math.round(hrrPctVal * 100) / 100
  };
}

function computeExercise(measurements: Measurement[]): Array<{
  type_name: string;
  date: string;
  time: string;
  duration_seconds: number;
  distance_meters: number;
  calories: number;
}> {
  const exM = measurements.filter((m) => m.data_type === 'exercise' && m.value_json);
  const sessions: Array<{
    type_name: string;
    date: string;
    time: string;
    duration_seconds: number;
    distance_meters: number;
    calories: number;
  }> = [];
  for (const m of exM) {
    try {
      if (!m.value_json) continue;
      const d = JSON.parse(m.value_json);
      sessions.push({
        type_name: (d.exercise_type_name ?? d.type_name ?? 'Exercise') as string,
        date: m.start_time.slice(0, 10),
        time: m.start_time.slice(11, 19),
        duration_seconds: (d.duration_seconds ?? d.duration ?? 0) as number,
        distance_meters: (d.distance_meters ?? d.distance ?? 0) as number,
        calories: (d.calories ?? 0) as number
      });
    } catch {
      /* skip */
    }
  }
  return sessions.slice(0, 5);
}

export function useAnalytics(rangeKey: string = '30d') {
  const data = liveQuery(async () => {
    const days = RANGE_DAYS[rangeKey] ?? 30;
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    const cutoffISO = cutoff.toISOString();

    const targetCodes = [
      'steps',
      'weight',
      'body_weight',
      'sleep',
      'exercise',
      'resting_heart_rate'
    ];
    const arrays = await Promise.all(
      targetCodes.map((code) =>
        db.measurement
          .where('[metric_code+start_time]')
          .between([code, cutoffISO], [code, Dexie.maxKey])
          .toArray()
      )
    );

    const measurements = arrays.flat().filter((m) => !m.deleted_at);
    return computeAnalytics(measurements, rangeKey);
  });

  return data;
}

function interpretCohens(d: number): string {
  const abs = Math.abs(d);
  if (abs >= 0.8) return 'large';
  if (abs >= 0.5) return 'medium';
  if (abs >= 0.2) return 'small';
  return 'negligible';
}

export function useCorrelations(
  rangeKey: string = '90d',
  method: 'pearson' | 'spearman' = 'pearson'
) {
  const data = liveQuery(async () => {
    const days = RANGE_DAYS[rangeKey] ?? 90;
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    const pivot = new Map<string, number[]>();

    await db.measurement
      .where('start_time')
      .above(cutoff.toISOString())
      .each((m) => {
        if (!m.deleted_at && m.value_numeric != null) {
          const dt = m.metric_code || m.data_type;
          let list = pivot.get(dt);
          if (!list) {
            list = [];
            pivot.set(dt, list);
          }
          list.push(m.value_numeric);
        }
      });

    const metrics = [...pivot.keys()].filter((k) => pivot.get(k)!.length >= 14);
    const pairs: Correlation[] = [];
    const pValues: number[] = [];
    const corrFunc = method === 'pearson' ? pearson : spearman;

    for (let i = 0; i < metrics.length; i++) {
      for (let j = i + 1; j < metrics.length; j++) {
        const xs = pivot.get(metrics[i])!;
        const ys = pivot.get(metrics[j])!;
        const n = Math.min(xs.length, ys.length);
        const pr = corrFunc(xs.slice(0, n), ys.slice(0, n));
        if (!pr || pr.n < 3) continue;
        pairs.push({
          metric_a: metrics[i],
          metric_b: metrics[j],
          pearson_r: pr.r,
          pearson_p: pr.p_value,
          p_adjusted_bh: 1.0,
          effect_size_d: Math.abs(pr.r),
          ci_lower: pr.ci_lower,
          ci_upper: pr.ci_upper,
          n: pr.n,
          interpretation: interpretCohens(Math.abs(pr.r))
        });
        pValues.push(pr.p_value);
      }
    }

    if (pairs.length > 0) {
      const fdr = benjaminiHochberg(pValues);
      for (let i = 0; i < pairs.length; i++) {
        pairs[i] = {
          ...pairs[i],
          p_adjusted_bh: fdr.adjusted[i],
          interpretation: fdr.rejected[i] ? pairs[i].interpretation : 'negligible'
        };
      }
    }

    return { pairs, n_comparisons: pairs.length, correction: 'Benjamini-Hochberg FDR' };
  });

  return data;
}

export interface TrendResult {
  values: number[];
  labels: string[];
  regression: {
    slope: number;
    intercept: number;
    r_squared: number;
    points: Array<{ x: number; y: number }>;
    ci: Array<{ x: number; lower: number; upper: number }>;
    n: number;
  } | null;
}

export function useTrend(metric: string, rangeKey: string = '90d') {
  const data = liveQuery(async () => {
    if (!metric) return { values: [], labels: [], regression: null };
    const days = RANGE_DAYS[rangeKey] ?? 90;
    const cutoff = new Date();
    cutoff.setDate(cutoff.getDate() - days);
    const cutoffISO = cutoff.toISOString();

    const dayMap = new Map<string, { sum: number; count: number }>();
    const rawValues: number[] = [];
    const rawLabels: string[] = [];
    let count = 0;

    await db.measurement
      .where('[metric_code+start_time]')
      .between([metric, cutoffISO], [metric, Dexie.maxKey])
      .each((m) => {
        if (!m.deleted_at && m.value_numeric != null) {
          count++;
          const day = m.start_time.split('T')[0];
          const existing = dayMap.get(day);
          if (existing) {
            existing.sum += m.value_numeric;
            existing.count += 1;
          } else {
            dayMap.set(day, { sum: m.value_numeric, count: 1 });
          }
          rawValues.push(m.value_numeric);
          rawLabels.push(m.start_time.slice(5));
        }
      });

    let values: number[];
    let labels: string[];

    if (count > 150) {
      labels = Array.from(dayMap.keys()).map((d) => d.slice(5));
      values = Array.from(dayMap.values()).map((v) => Math.round((v.sum / v.count) * 10) / 10);
    } else {
      values = rawValues;
      labels = rawLabels;
    }

    if (values.length < 3) return { values, labels, regression: null };

    const xs = values.map((_, i) => i);
    const reg = linearRegression(xs, values);
    if (!reg) return { values, labels, regression: null };

    const regPoints = xs.map((x) => ({
      x,
      y: reg.intercept + reg.slope * x
    }));
    const ci = xs.map((x) => {
      const pi = predictionInterval(reg, x);
      return {
        x,
        lower: pi?.lower ?? reg.intercept + reg.slope * x,
        upper: pi?.upper ?? reg.intercept + reg.slope * x
      };
    });

    return {
      values,
      labels,
      regression: {
        slope: reg.slope,
        intercept: reg.intercept,
        r_squared: reg.r_squared,
        points: regPoints,
        ci,
        n: reg.n
      }
    };
  });
  return data;
}

export function useWellness(dateStr?: string) {
  const data = liveQuery(async () => {
    const target = dateStr ? new Date(dateStr) : new Date();
    const since = new Date(target);
    since.setDate(since.getDate() - 28);
    const sinceISO = since.toISOString();
    const untilISO = new Date(target.getTime() + 86400000).toISOString();

    const targetCodes = ['resting_heart_rate', 'heart_rate', 'steps', 'sleep'];
    const arrays = await Promise.all(
      targetCodes.map((code) =>
        db.measurement
          .where('[metric_code+start_time]')
          .between([code, sinceISO], [code, untilISO], true, false)
          .toArray()
      )
    );

    const measurements = arrays.flat().filter((m) => !m.deleted_at && m.value_numeric != null);

    const hrVals = measurements
      .filter(
        (m) =>
          m.data_type === 'heart_rate' ||
          m.metric_code === 'heart_rate' ||
          m.metric_code === 'resting_heart_rate'
      )
      .map((m) => m.value_numeric!);
    const stepVals = measurements
      .filter((m) => m.data_type === 'steps' || m.metric_code === 'steps')
      .map((m) => m.value_numeric!);
    const sleepVals = measurements
      .filter(
        (m) => (m.data_type === 'sleep' || m.metric_code === 'sleep') && m.value_numeric != null
      )
      .map((m) => m.value_numeric!);

    const muHr = hrVals.length > 0 ? hrVals.reduce((a, b) => a + b, 0) / hrVals.length : 60;
    const sigHr =
      hrVals.length > 1
        ? Math.sqrt(hrVals.reduce((a, v) => a + (v - muHr) ** 2, 0) / (hrVals.length - 1))
        : 5;
    const muSteps =
      stepVals.length > 0 ? stepVals.reduce((a, b) => a + b, 0) / stepVals.length : 8000;
    const sigSteps =
      stepVals.length > 1
        ? Math.sqrt(stepVals.reduce((a, v) => a + (v - muSteps) ** 2, 0) / (stepVals.length - 1))
        : 2000;
    const muSleep =
      sleepVals.length > 0 ? sleepVals.reduce((a, b) => a + b, 0) / sleepVals.length : 7;
    const sigSleep =
      sleepVals.length > 1
        ? Math.sqrt(sleepVals.reduce((a, v) => a + (v - muSleep) ** 2, 0) / (sleepVals.length - 1))
        : 1;

    const todayRhr = hrVals.length > 0 ? hrVals[hrVals.length - 1] : muHr;
    const todaySteps = stepVals.length > 0 ? stepVals[stepVals.length - 1] : muSteps;
    const todaySleep = sleepVals.length > 0 ? sleepVals[sleepVals.length - 1] : muSleep;

    const score = recoveryComposite(todaySleep, 50.0, todayRhr, Math.round(todaySteps), {
      sleep: [muSleep, Math.max(sigSleep, 0.01)],
      hrv: [50.0, 10.0],
      resting_hr: [muHr, Math.max(sigHr, 0.01)],
      log_steps: [muSteps, Math.max(sigSteps, 0.01)]
    });

    return {
      score: Math.round(score.score * 10) / 10,
      interpretation: score.interpretation,
      sleep_z: Math.round(score.sleep_z * 100) / 100,
      hrv_z: Math.round(score.hrv_z * 100) / 100,
      hr_z: Math.round(score.hr_z * 100) / 100,
      steps_z: Math.round(score.steps_z * 100) / 100
    };
  });
  return data;
}

export function useGoalForecast(goalId: string) {
  const data = liveQuery(async () => {
    const goal = await db.goal.get(goalId);
    if (!goal || !goal.metric_code) return null;
    const measurements = await db.measurement
      .where('metric_code')
      .equals(goal.metric_code)
      .filter((m) => !m.deleted_at && m.value_numeric != null)
      .toArray();

    measurements.sort(
      (a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
    );

    const values = measurements.map((m) => m.value_numeric!);
    if (values.length < 3 || !goal.deadline) return null;

    const startDate = new Date(goal.created_at || measurements[0].start_time);
    const deadlineDate = new Date(goal.deadline);
    const daysTotal = Math.round((deadlineDate.getTime() - startDate.getTime()) / 86400000);
    if (daysTotal <= 0) return null;

    const xs = measurements.map((m) =>
      Math.round((new Date(m.start_time).getTime() - startDate.getTime()) / 86400000)
    );
    const reg = linearRegression(xs, values);
    if (!reg) return null;

    const pi = predictionInterval(reg, daysTotal, 0.8);

    return {
      goal_id: goalId,
      target: goal.target_value,
      direction: goal.direction,
      deadline: goal.deadline,
      predicted: pi ? Math.round(pi.point_estimate * 100) / 100 : null,
      ci_lower: pi ? Math.round(pi.lower * 100) / 100 : null,
      ci_upper: pi ? Math.round(pi.upper * 100) / 100 : null,
      r_squared: Math.round(reg.r_squared * 10000) / 10000,
      n: reg.n
    };
  });
  return data;
}

export function useSleepDebt(age: number = 30) {
  const data = liveQuery(async () => {
    const rawRecent = await db.measurement
      .where('[metric_code+start_time]')
      .between(['sleep', Dexie.minKey], ['sleep', Dexie.maxKey])
      .reverse()
      .limit(28)
      .toArray();

    const recent = rawRecent.filter((m) => !m.deleted_at);

    const durations: number[] = [];
    for (const m of recent.slice(0, 28)) {
      if (m.value_numeric != null) {
        durations.push(m.value_numeric);
      } else if (m.value_json) {
        try {
          const d = JSON.parse(m.value_json);
          const dur = (d.duration_seconds ?? 0) / 3600;
          if (dur > 0) durations.push(dur);
        } catch {
          /* skip */
        }
      }
    }

    if (durations.length < 3) return null;
    const debt = sleepDebtCumulative(durations, age);
    return {
      debt: debt.debt.map((v) => Math.round(v * 100) / 100),
      baseline_h: debt.baseline_h,
      cumulative_last: Math.round(debt.debt[debt.debt.length - 1] * 100) / 100
    };
  });
  return data;
}

function getUserHeight(): number {
  try {
    const stored = localStorage.getItem('salus_user');
    if (stored) {
      const user = JSON.parse(stored);
      if (user.height_cm && user.height_cm > 0) return user.height_cm;
    }
  } catch {
    /* ignore */
  }
  return 170;
}
