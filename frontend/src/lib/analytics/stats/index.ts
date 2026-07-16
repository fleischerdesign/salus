export type {
  Baselines,
  BootstrapCI,
  Correlation,
  EffectSize,
  EfficiencyResult,
  Fatigue,
  FDR,
  Forecast,
  HRV,
  OneRMResult,
  PI,
  Progression,
  Readings,
  RecoveryScore,
  Regression,
  SleepDebtResult,
  TrendTest
} from './types';

export {
  erf,
  incompleteBeta,
  lnGamma,
  normalCdf,
  normalPpf,
  quantile,
  rank,
  tCdf,
  tPpf,
  xorshift64,
  yuleWalkerAR1
} from './internal';
import {
  incompleteBeta,
  normalCdf,
  quantile,
  rank,
  tPpf,
  xorshift64,
  yuleWalkerAR1
} from './internal';
import * as T from './types';

export function mean(xs: number[]): number | null {
  if (xs.length === 0) return null;
  let s = 0.0;
  for (const x of xs) s += x;
  return s / xs.length;
}

export function variance(xs: number[]): number | null {
  const n = xs.length;
  if (n < 2) return null;
  const m = xs.reduce((a, b) => a + b, 0) / n;
  let s2 = 0.0;
  for (const x of xs) {
    const diff = x - m;
    s2 += diff * diff;
  }
  return s2 / (n - 1);
}

export function std(xs: number[]): number | null {
  const v = variance(xs);
  if (v === null) return null;
  return Math.sqrt(v);
}

export function covariance(xs: number[], ys: number[]): number | null {
  const n = xs.length;
  if (n !== ys.length || n < 2) return null;
  const mx = xs.reduce((a, b) => a + b, 0) / n;
  const my = ys.reduce((a, b) => a + b, 0) / n;
  let s = 0.0;
  for (let i = 0; i < n; i++) s += (xs[i] - mx) * (ys[i] - my);
  return s / (n - 1);
}

export function quantileRank(xs: number[], x: number): number | null {
  if (xs.length === 0) return null;
  const n = xs.length;
  let countLt = 0;
  let countEq = 0;
  for (const v of xs) {
    if (v < x) countLt++;
    else if (v === x) countEq++;
  }
  if (countEq === 0) return countLt / n;
  return (countLt + 0.5 * countEq) / n;
}

export function rollingMean(xs: number[], window: number): (number | null)[] {
  const n = xs.length;
  const result: (number | null)[] = new Array(n).fill(null);
  if (window < 1 || n < window) return result;
  let wsum = xs.slice(0, window).reduce((a, b) => a + b, 0);
  result[window - 1] = wsum / window;
  for (let i = window; i < n; i++) {
    wsum = wsum + xs[i] - xs[i - window];
    result[i] = wsum / window;
  }
  return result;
}

export function rollingStd(xs: number[], window: number): (number | null)[] {
  const n = xs.length;
  const result: (number | null)[] = new Array(n).fill(null);
  if (window < 2 || n < window) return result;
  for (let i = window - 1; i < n; i++) {
    const chunk = xs.slice(i - window + 1, i + 1);
    result[i] = std(chunk);
  }
  return result;
}

export function rollingZscore(xs: number[], window: number): (number | null)[] {
  const n = xs.length;
  const result: (number | null)[] = new Array(n).fill(null);
  if (window < 2 || n < window) return result;
  const rMean = rollingMean(xs, window);
  const rStd = rollingStd(xs, window);
  for (let i = 0; i < n; i++) {
    if (rMean[i] !== null && rStd[i] !== null && rStd[i] !== 0) {
      result[i] = (xs[i] - rMean[i]!) / rStd[i]!;
    }
  }
  return result;
}

export function linearRegression(xs: number[], ys: number[]): T.Regression | null {
  const n = xs.length;
  if (n !== ys.length || n < 2) return null;
  const xStd = std(xs);
  if (xStd === null || xStd === 0.0) return null;
  const xMean = xs.reduce((a, b) => a + b, 0) / n;
  const yMean = ys.reduce((a, b) => a + b, 0) / n;
  const covVal = covariance(xs, ys);
  if (covVal === null) return null;
  const slope = covVal / (xStd * xStd);
  const intercept = yMean - slope * xMean;
  const residuals = ys.map((y, i) => y - (intercept + slope * xs[i]));
  const df = n - 2;
  const sse = residuals.reduce((a, e) => a + e * e, 0);
  const see = df > 0 ? Math.sqrt(sse / df) : 0.0;
  const yVar = ys.reduce((a, y) => a + (y - yMean) ** 2, 0);
  const rSquared = Math.max(0.0, Math.min(1.0, yVar > 0 ? 1.0 - sse / yVar : 0.0));
  const ssx = xStd * xStd * (n - 1);
  return {
    slope,
    intercept,
    r_squared: rSquared,
    standard_error: see,
    n,
    residuals,
    df,
    x_mean: xMean,
    ssx
  };
}

export function predictionInterval(
  reg: T.Regression,
  xNew: number,
  confidence: number = 0.95
): T.PI | null {
  if (reg.n < 3) return null;
  const pe = reg.intercept + reg.slope * xNew;
  const alpha = 1.0 - confidence;
  const tCrit = reg.df > 0 ? tPpf(1.0 - alpha / 2.0, reg.df) : 1.96;
  const sePred =
    reg.standard_error *
    Math.sqrt(1.0 + 1.0 / reg.n + (xNew - reg.x_mean) ** 2 / Math.max(reg.ssx, 1e-12));
  const margin = tCrit * sePred;
  return { lower: pe - margin, upper: pe + margin, point_estimate: pe, confidence };
}

function zCritical(confidence: number): number {
  const map: Record<number, number> = { 0.9: 1.645, 0.95: 1.96, 0.99: 2.576 };
  return map[confidence] ?? 1.96;
}

export function pearson(xs: number[], ys: number[]): T.Correlation | null {
  const n = xs.length;
  if (n !== ys.length || n < 3) return null;
  const xStd = std(xs);
  const yStd = std(ys);
  if (xStd === null || yStd === null || xStd === 0.0 || yStd === 0.0) return null;
  const mX = xs.reduce((a, b) => a + b, 0) / n;
  const mY = ys.reduce((a, b) => a + b, 0) / n;
  const num = xs.reduce((s, _x, i) => s + (xs[i] - mX) * (ys[i] - mY), 0);
  const den = Math.sqrt(
    xs.reduce((s, x) => s + (x - mX) ** 2, 0) * ys.reduce((s, y) => s + (y - mY) ** 2, 0)
  );
  if (den === 0.0) return null;
  const r = Math.max(-1.0, Math.min(1.0, num / den));
  const df = n - 2;
  let tStat: number;
  let pVal: number;
  if (Math.abs(r) >= 1.0 - 1e-15) {
    tStat = r >= 0 ? Infinity : -Infinity;
    pVal = 0.0;
  } else {
    tStat = r * Math.sqrt(df / (1.0 - r * r));
    const xBeta = df / (df + tStat * tStat);
    const ib = incompleteBeta(df / 2.0, 0.5, xBeta);
    pVal = tStat >= 0 ? ib : 2.0 - ib;
    pVal = Math.max(0.0, Math.min(1.0, pVal));
  }
  const zFisher = Math.abs(r) < 1.0 ? Math.atanh(r) : Math.sign(r) * Infinity;
  const seZ = 1.0 / Math.sqrt(n - 3);
  const zAlpha = zCritical(0.95);
  const ciLower = Math.tanh(zFisher - zAlpha * seZ);
  const ciUpper = Math.tanh(zFisher + zAlpha * seZ);
  return {
    r,
    n,
    t_statistic: tStat,
    p_value: pVal,
    ci_lower: Math.max(-1.0, Math.min(1.0, ciLower)),
    ci_upper: Math.max(-1.0, Math.min(1.0, ciUpper)),
    df
  };
}

export function spearman(xs: number[], ys: number[]): T.Correlation {
  const rx = rank([...xs]);
  const ry = rank([...ys]);
  return pearson(rx, ry)!;
}

export function cohensDPaired(x: number[], y: number[]): T.EffectSize | null {
  const n = x.length;
  if (n !== y.length || n < 2) return null;
  const diffs = x.map((xi, i) => xi - y[i]);
  const dMean = diffs.reduce((a, b) => a + b, 0) / n;
  const dSd = Math.sqrt(diffs.reduce((a, d) => a + (d - dMean) ** 2, 0) / (n - 1));
  if (dSd === 0.0)
    return { d: 0.0, hedges_g: 0.0, ci_lower: 0.0, ci_upper: 0.0, n, interpretation: 'negligible' };
  const dVal = dMean / dSd;
  let hedgesG = dVal;
  if (n < 20) hedgesG = dVal * (1.0 - 3.0 / (4.0 * n - 9.0));
  const seD = Math.sqrt(1.0 / n + (dVal * dVal) / (2.0 * n));
  const zCrit = zCritical(0.95);
  const ciLower = dVal - zCrit * seD;
  const ciUpper = dVal + zCrit * seD;
  const absD = Math.abs(dVal);
  let interp = 'negligible';
  if (absD >= 0.8) interp = 'large';
  else if (absD >= 0.5) interp = 'medium';
  else if (absD >= 0.2) interp = 'small';
  return {
    d: dVal,
    hedges_g: hedgesG,
    ci_lower: ciLower,
    ci_upper: ciUpper,
    n,
    interpretation: interp
  };
}

export function benjaminiHochberg(pValues: number[], alpha: number = 0.05): T.FDR {
  const m = pValues.length;
  const indexed = pValues.map((p, i) => ({ p, i })).sort((a, b) => a.p - b.p);
  const adjSorted = indexed.map((item, rank) => Math.min((item.p * m) / (rank + 1), 1.0));
  for (let i = adjSorted.length - 2; i >= 0; i--)
    adjSorted[i] = Math.min(adjSorted[i], adjSorted[i + 1]);
  const adjusted = new Array<number>(m);
  const rejected = new Array<boolean>(m);
  for (let rank = 0; rank < indexed.length; rank++) {
    adjusted[indexed[rank].i] = adjSorted[rank];
    rejected[indexed[rank].i] = adjSorted[rank] <= alpha;
  }
  return { adjusted, rejected, alpha, method: 'Benjamini-Hochberg FDR' };
}

export function mannKendall(series: number[]): T.TrendTest | null {
  const n = series.length;
  if (n < 3) return null;
  let s = 0;
  for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) s += Math.sign(series[j] - series[i]);
  const counts = new Map<number, number>();
  for (const v of series) counts.set(v, (counts.get(v) ?? 0) + 1);
  let tieCorrection = 0.0;
  for (const t of counts.values()) {
    if (t > 1) tieCorrection += t * (t - 1) * (2 * t + 5);
  }
  const varS = Math.max((n * (n - 1) * (2 * n + 5) - tieCorrection) / 18.0, 1e-12);
  let z: number;
  if (s > 0) z = (s - 1.0) / Math.sqrt(varS);
  else if (s < 0) z = (s + 1.0) / Math.sqrt(varS);
  else z = 0.0;
  const pVal = 2.0 * (1.0 - normalCdf(Math.abs(z)));
  const tau = s / ((n * (n - 1)) / 2.0);
  let trend = 'none';
  if (pVal < 0.05 && z > 0) trend = 'increasing';
  else if (pVal < 0.05 && z < 0) trend = 'decreasing';
  return { s, z, p_value: pVal, trend, n, tau };
}

export function bootstrapCi(
  xs: number[],
  statistic: (sample: number[]) => number,
  nIter: number = 1000,
  seed: number = 42,
  confidence: number = 0.95
): T.BootstrapCI | null {
  const n = xs.length;
  if (n < 2) return null;
  const pointEst = statistic(xs);
  let seedState = seed;
  const stats: number[] = [];
  for (let i = 0; i < nIter; i++) {
    const sample = new Array<number>(n);
    for (let j = 0; j < n; j++) {
      const [rnd, next] = xorshift64(seedState);
      seedState = next;
      sample[j] = xs[Math.floor(rnd * n)];
    }
    stats.push(statistic(sample));
  }
  const tail = (1.0 - confidence) / 2.0;
  const lower = quantile(stats, tail) ?? pointEst;
  const upper = quantile(stats, 1.0 - tail) ?? pointEst;
  return { lower, upper, point_estimate: pointEst, n_iter: nIter, confidence, seed };
}

export function ewmaForecast(
  series: number[],
  alpha: number = 0.3,
  horizon: number = 1
): T.Forecast | null {
  const n = series.length;
  if (n < 2 || !(alpha > 0.0 && alpha < 1.0)) return null;
  const fitted = [series[0]];
  for (let i = 1; i < n; i++) fitted.push(alpha * series[i - 1] + (1.0 - alpha) * fitted[i - 1]);
  const residuals = series.map((s, i) => s - fitted[i]);
  const residualsShort = residuals.slice(1);
  const yw = yuleWalkerAR1(residualsShort);
  const phi = yw !== null ? yw[0] : 0.0;
  const point = [...series];
  for (let h = 1; h <= horizon; h++) {
    const fw = alpha * series[n - 1] + (1.0 - alpha) * fitted[n - 1] + phi * residuals[n - 1];
    point.push(fw);
  }
  const mapeVal = mape(series.slice(1), fitted.slice(1));
  return { point, fitted, residuals, mape: mapeVal, alpha, horizon, n_train: n };
}

export function mape(yTrue: number[], yPred: number[]): number | null {
  const n = yTrue.length;
  if (n !== yPred.length || n === 0) return null;
  for (const y of yTrue) {
    if (y === 0.0) return null;
  }
  const absPct = yTrue.map((yt, i) => Math.abs((yt - yPred[i]) / yt));
  return (absPct.reduce((a, b) => a + b, 0) / n) * 100.0;
}

export function restingHrWindowed(
  readings: { timestamp: number; bpm: number }[],
  wakeTs: number,
  windowMin: number = 5.0
): number | null {
  const windowRange = [...readings];
  const windowSec = windowMin * 60.0;
  const inWindow = windowRange.filter(
    (r) => wakeTs <= r.timestamp && r.timestamp <= wakeTs + 30.0 * 60.0
  );
  if (inWindow.length < 2) return null;
  let minMA = Infinity;
  for (let start = 0; start < inWindow.length; start++) {
    const mid = inWindow[start].timestamp + windowSec / 2.0;
    const vals: number[] = [];
    for (const r of inWindow) {
      if (Math.abs(r.timestamp - mid) <= windowSec / 2.0) vals.push(r.bpm);
    }
    if (vals.length >= 2) {
      const ma = vals.reduce((a, b) => a + b, 0) / vals.length;
      if (ma < minMA) minMA = ma;
    }
  }
  return minMA !== Infinity ? minMA : null;
}

export function sleepEfficiency(tstMin: number, tibMin: number): T.EfficiencyResult {
  if (tibMin === 0.0) return { efficiency: 0.0, warning: 'TIB was zero' };
  return { efficiency: Math.max(0.0, Math.min(1.0, tstMin / tibMin)), warning: null };
}

export function sleepDebtCumulative(durationsH: number[], ageY: number): T.SleepDebtResult {
  const baselineH = ageY >= 65 ? 7.5 : 8.0;
  const debt: number[] = [];
  let cum = 0.0;
  for (const d of durationsH) {
    cum += baselineH - d;
    debt.push(cum);
  }
  return { debt, baseline_h: baselineH };
}

export function hrvTimeDomain(rrIntervalsMs: number[]): T.HRV | null {
  const n = rrIntervalsMs.length;
  if (n < 2) return null;
  const m = rrIntervalsMs.reduce((a, b) => a + b, 0) / n;
  const sdnn = Math.sqrt(rrIntervalsMs.reduce((a, rr) => a + (rr - m) ** 2, 0) / (n - 1));
  const diffs: number[] = [];
  for (let i = 1; i < n; i++) diffs.push(rrIntervalsMs[i] - rrIntervalsMs[i - 1]);
  const rmssd = Math.sqrt(diffs.reduce((a, d) => a + d * d, 0) / diffs.length);
  const pnn50 = diffs.filter((d) => Math.abs(d) > 50.0).length / diffs.length;
  return { mean_rr: m, sdnn, rmssd, pnn50, n };
}

export function rmssdToScore(rmssd: number, meanRmssd: number, stdRmssd: number): number {
  if (stdRmssd === 0.0) return 50.0;
  const z = (Math.log(Math.max(rmssd, 1e-9)) - Math.log(Math.max(meanRmssd, 1e-9))) / stdRmssd;
  return Math.max(0.0, Math.min(100.0, 50.0 + 10.0 * z));
}

export function recoveryComposite(
  sleepScore: number,
  hrvRmssd: number,
  restingHr: number,
  steps: number,
  baselines: T.Baselines
): T.RecoveryScore {
  const [muSleep, sigSleep] = baselines['sleep'] ?? [7.0, 1.0];
  const [muHrv, sigHrv] = baselines['hrv'] ?? [50.0, 10.0];
  const [muHr, sigHr] = baselines['resting_hr'] ?? [60.0, 5.0];
  const [muSteps, sigSteps] = baselines['log_steps'] ?? [8.0, 1.0];
  const zSleep = (sleepScore - muSleep) / Math.max(sigSleep, 1e-9);
  const zHrv = (hrvRmssd - muHrv) / Math.max(sigHrv, 1e-9);
  const zHr = -(restingHr - muHr) / Math.max(sigHr, 1e-9);
  const zSteps = (Math.log(Math.max(steps, 1)) - muSteps) / Math.max(sigSteps, 1e-9);
  let score = 50.0 + 10.0 * (0.35 * zSleep + 0.3 * zHrv + 0.2 * zHr + 0.15 * zSteps);
  score = Math.max(0.0, Math.min(100.0, score));
  let interp = 'underrecovered';
  if (score >= 75) interp = 'primed';
  else if (score >= 50) interp = 'moderate';
  return {
    score,
    interpretation: interp,
    sleep_z: zSleep,
    hrv_z: zHrv,
    hr_z: zHr,
    steps_z: zSteps
  };
}

export function bmrCunningham(weightKg: number, bodyFatPct: number | null): number | null {
  if (bodyFatPct === null || bodyFatPct < 0.0 || bodyFatPct >= 1.0) return null;
  return 500.0 + 22.0 * weightKg * (1.0 - bodyFatPct);
}

export function bmrMifflinStJeor(
  weightKg: number,
  heightCm: number,
  ageY: number,
  sex: string | null
): number {
  const base = 10.0 * weightKg + 6.25 * heightCm - 5.0 * ageY;
  if (sex === 'male') return base + 5.0;
  return base - 161.0;
}

export function hrMaxTanaka(ageY: number): number {
  return 208.0 - 0.7 * ageY;
}

export function hrrPct(hrAvgAwake: number, hrResting: number, hrMax: number): number {
  if (hrMax === hrResting) return 0.05;
  return Math.max(0.05, Math.min(0.85, (hrAvgAwake - hrResting) / (hrMax - hrResting)));
}

export function palFromHrr(hrrPct: number, calibrationFactor: number = 1.5): number {
  return Math.max(1.0, Math.min(2.5, 1.0 + hrrPct * calibrationFactor));
}

export function tefFromMacros(proteinG: number, carbsG: number, fatG: number): number {
  return proteinG * 4.0 * 0.25 + carbsG * 4.0 * 0.06 + fatG * 9.0 * 0.02;
}

export function tdee(bmr: number, pal: number, tef: number): number {
  return Math.round(bmr * pal + tef);
}

export function epley1RM(weight: number, reps: number): number {
  return weight * (1.0 + reps / 30.0);
}

export function brzycki1RM(weight: number, reps: number): number | null {
  if (reps > 10) return null;
  return (weight * 36.0) / (37.0 - reps);
}

export function oneRmRegression(
  sets: [number, number][],
  method: string = 'epley'
): T.OneRMResult | null {
  if (sets.length < 1) return null;
  const transformer = method === 'epley' ? epley1RM : brzycki1RM;
  const estimates: number[] = [];
  for (const [weight, reps] of sets) {
    const est = transformer(weight, reps);
    if (est !== null) estimates.push(est);
  }
  if (estimates.length === 0) return null;
  const oneRm = estimates.reduce((a, b) => a + b, 0) / estimates.length;
  let ciLower = oneRm;
  let ciUpper = oneRm;
  if (estimates.length >= 3) {
    const bc = bootstrapCi(estimates, (xs) => mean(xs) ?? 0, 500, 42);
    if (bc) {
      ciLower = bc.lower;
      ciUpper = bc.upper;
    }
  }
  const xsIdx = estimates.map((_, i) => i);
  const reg = linearRegression(xsIdx.map(Number), estimates);
  return {
    one_rm: oneRm,
    ci_lower: ciLower,
    ci_upper: ciUpper,
    n_sets: sets.length,
    r_squared: reg?.r_squared ?? 0.0
  };
}

export function tonnageProgression(sessions: [number, number][]): T.Progression | null {
  if (sessions.length < 2) return null;
  const weeks = sessions.map(([w]) => w);
  const tonnages = sessions.map(([, t]) => t);
  const reg = linearRegression(weeks, tonnages);
  if (reg === null) return null;
  const mk = mannKendall(tonnages);
  const isPlateaued = mk !== null ? mk.p_value > 0.05 && reg.r_squared < 0.2 : false;
  const se = reg.standard_error;
  const ciMargin = (1.96 * se) / Math.sqrt(Math.max(reg.n, 1));
  return {
    slope_kg_per_week: reg.slope,
    slope_ci: [reg.slope - ciMargin, reg.slope + ciMargin],
    r_squared: reg.r_squared,
    mann_kendall: mk ?? { s: 0, z: 0, p_value: 1.0, trend: 'none', n: 0, tau: 0 },
    is_plateaued: isPlateaued
  };
}

export function fatigueEmwa(
  dailyLoad: number[],
  decayPositive: number = 1.0 / 6.0,
  decayNegative: number = 1.0 / 6.0
): T.Fatigue | null {
  const n = dailyLoad.length;
  if (n === 0) return null;
  const fitness = new Array<number>(n);
  const fatigue = new Array<number>(n);
  const performance = new Array<number>(n);
  for (let i = 0; i < n; i++) {
    if (i === 0) {
      fitness[i] = dailyLoad[i] * decayPositive;
      fatigue[i] = dailyLoad[i] * decayNegative;
    } else {
      fitness[i] = dailyLoad[i] * decayPositive + fitness[i - 1] * (1.0 - decayPositive);
      fatigue[i] = dailyLoad[i] * decayNegative + fatigue[i - 1] * (1.0 - decayNegative);
    }
    performance[i] = fitness[i] - fatigue[i];
  }
  return { fitness, fatigue, performance };
}

export function changePointPelt(
  series: number[],
  penalty: string = 'BIC'
): { indices: number[]; costs: number[] } | null {
  const n = series.length;
  if (n < 2) return null;
  const meanAll = series.reduce((a, b) => a + b, 0) / n;
  const varEst = n > 1 ? series.reduce((a, x) => a + (x - meanAll) ** 2, 0) / (n - 1) : 1.0;
  const pen =
    penalty === 'BIC'
      ? Math.log(n) * varEst
      : n > 1
        ? Math.log(n) + Math.log(n - 1)
        : Math.log(n) * varEst;
  const cost = new Array<number>(n + 1).fill(Infinity);
  cost[0] = -pen;
  const cpList: number[] = [];
  const lastCp = new Array<number>(n + 1).fill(0);
  let R: number[] = [];
  for (let t = 1; t <= n; t++) {
    let bestCost = Infinity;
    let bestCp = 0;
    const nextR: number[] = [0];
    const checkSet = R.length > 0 ? R : [0];
    for (const s of checkSet) {
      const seg = series.slice(s, t);
      const segLen = seg.length;
      if (segLen < 1) continue;
      const segMean = seg.reduce((a, b) => a + b, 0) / segLen;
      const segCost = seg.reduce((a, x) => a + (x - segMean) ** 2, 0);
      const total = cost[s] + segCost + pen;
      if (total < bestCost) {
        bestCost = total;
        bestCp = s;
      }
      if (total <= cost[t] + pen) {
        nextR.push(s);
        if (nextR.length > 50) break;
      }
    }
    R = [...new Set(nextR)];
    cost[t] = bestCost;
    lastCp[t] = bestCp;
  }
  let pos = n;
  while (pos > 0 && lastCp[pos] > 0) {
    cpList.push(lastCp[pos]);
    pos = lastCp[pos];
  }
  cpList.sort((a, b) => a - b);
  return { indices: cpList, costs: cost };
}
