interface Regression {
  readonly slope: number;
  readonly intercept: number;
  readonly r_squared: number;
  readonly standard_error: number;
  readonly n: number;
  readonly residuals: readonly number[];
  readonly df: number;
  readonly x_mean: number;
  readonly ssx: number;
}

interface PI {
  readonly lower: number;
  readonly upper: number;
  readonly point_estimate: number;
  readonly confidence: number;
}

interface Correlation {
  readonly r: number;
  readonly n: number;
  readonly t_statistic: number;
  readonly p_value: number;
  readonly ci_lower: number;
  readonly ci_upper: number;
  readonly df: number;
}

interface EffectSize {
  readonly d: number;
  readonly hedges_g: number;
  readonly ci_lower: number;
  readonly ci_upper: number;
  readonly n: number;
  readonly interpretation: string;
}

interface FDR {
  readonly adjusted: readonly number[];
  readonly rejected: readonly boolean[];
  readonly alpha: number;
  readonly method: string;
}

interface TrendTest {
  readonly s: number;
  readonly z: number;
  readonly p_value: number;
  readonly trend: string;
  readonly n: number;
  readonly tau: number;
}

interface BootstrapCI {
  readonly lower: number;
  readonly upper: number;
  readonly point_estimate: number;
  readonly n_iter: number;
  readonly confidence: number;
  readonly seed: number;
}

interface Forecast {
  readonly point: readonly number[];
  readonly fitted: readonly number[];
  readonly residuals: readonly number[];
  readonly mape: number | null;
  readonly alpha: number;
  readonly horizon: number;
  readonly n_train: number;
}

interface EfficiencyResult {
  readonly efficiency: number;
  readonly warning: string | null;
}

interface SleepDebtResult {
  readonly debt: readonly number[];
  readonly baseline_h: number;
}

interface HRV {
  readonly mean_rr: number;
  readonly sdnn: number;
  readonly rmssd: number;
  readonly pnn50: number;
  readonly n: number;
}

interface RecoveryScore {
  readonly score: number;
  readonly interpretation: string;
  readonly sleep_z: number;
  readonly hrv_z: number;
  readonly hr_z: number;
  readonly steps_z: number;
}

interface OneRMResult {
  readonly one_rm: number;
  readonly ci_lower: number;
  readonly ci_upper: number;
  readonly n_sets: number;
  readonly r_squared: number;
}

interface Progression {
  readonly slope_kg_per_week: number;
  readonly slope_ci: readonly [number, number];
  readonly r_squared: number;
  readonly mann_kendall: TrendTest;
  readonly is_plateaued: boolean;
}

interface Fatigue {
  readonly fitness: readonly number[];
  readonly fatigue: readonly number[];
  readonly performance: readonly number[];
}

type Readings = readonly { readonly timestamp: number; readonly bpm: number }[];
type Baselines = Record<string, [number, number]>;

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
};
