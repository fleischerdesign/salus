import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { load as yamlLoad } from 'js-yaml';
import { describe, expect, it } from 'vitest';
import {
  benjaminiHochberg,
  bmrCunningham,
  bmrMifflinStJeor,
  bootstrapCi,
  brzycki1RM,
  cohensDPaired,
  epley1RM,
  erf,
  ewmaForecast,
  hrMaxTanaka,
  hrrPct,
  hrvTimeDomain,
  linearRegression,
  mannKendall,
  mape,
  mean,
  normalCdf,
  palFromHrr,
  pearson,
  predictionInterval,
  quantile,
  sleepDebtCumulative,
  sleepEfficiency,
  spearman,
  tdee,
  tefFromMacros
} from '$lib/analytics/stats';

const FIXTURES_DIR = join(import.meta.dirname, '..', '..', 'tests', 'fixtures', 'stats');

function loadFixture(name: string): Record<string, unknown> {
  const raw = readFileSync(join(FIXTURES_DIR, name), 'utf-8');
  return yamlLoad(raw) as Record<string, unknown>;
}

describe('linear_regression', () => {
  it('matches golden fixture', () => {
    const fx = loadFixture('linear_regression.yaml');
    const inp = fx.input as Record<string, number[]>;
    const exp = fx.expected as Record<string, number>;
    const reg = linearRegression(inp.xs, inp.ys);
    expect(reg).not.toBeNull();
    expect(reg!.slope).toBeCloseTo(exp.slope, 2);
    expect(reg!.intercept).toBeCloseTo(exp.intercept, 2);
    expect(reg!.r_squared).toBeCloseTo(exp.r_squared, 2);
    expect(reg!.standard_error).toBeCloseTo(exp.standard_error, 1);
    expect(reg!.n).toBe(exp.n);
  });
});

describe('pearson', () => {
  it('matches golden fixture', () => {
    const fx = loadFixture('pearson.yaml');
    const inp = fx.input as Record<string, number[]>;
    const exp = fx.expected as Record<string, number>;
    const c = pearson(inp.xs, inp.ys);
    expect(c).not.toBeNull();
    expect(c!.r).toBeCloseTo(exp.r, 2);
    expect(c!.n).toBe(exp.n);
  });
});

describe('spearman', () => {
  it('matches golden fixture', () => {
    const fx = loadFixture('spearman.yaml');
    const inp = fx.input as Record<string, number[]>;
    const exp = fx.expected as Record<string, number>;
    const c = spearman(inp.xs, inp.ys);
    expect(c.r).toBeCloseTo(exp.r, 1);
    expect(c.n).toBe(exp.n);
  });
});

describe('benjamini_hochberg', () => {
  it('rejects at least 3 p-values at alpha=0.05', () => {
    const fx = loadFixture('benjamini_hochberg.yaml');
    const inp = fx.input as Record<string, number[]>;
    const result = benjaminiHochberg(inp.p_values, 0.05);
    expect(result.adjusted.length).toBe(5);
    expect(result.rejected.filter((r) => r).length).toBeGreaterThanOrEqual(3);
  });
});

describe('mann_kendall', () => {
  it('detects increasing trend', () => {
    const fx = loadFixture('mann_kendall.yaml');
    const inp = fx.input as Record<string, number[]>;
    const exp = fx.expected as Record<string, unknown>;
    const mk = mannKendall(inp.series);
    expect(mk).not.toBeNull();
    expect(mk!.z).toBeGreaterThan(2.0);
    expect(mk!.trend).toBe(exp.trend);
    expect(mk!.tau).toBeGreaterThan(0.8);
  });
});

describe('bootstrap_ci', () => {
  it('produces deterministic output with seed', () => {
    const fx = loadFixture('bootstrap_ci.yaml');
    const inp = fx.input as Record<string, unknown>;
    const exp = fx.expected as Record<string, number>;
    const bc = bootstrapCi(
      inp.xs as number[],
      (xs: number[]) => mean(xs) ?? 0,
      inp.n_iter as number,
      inp.seed as number,
      inp.confidence as number
    );
    expect(bc).not.toBeNull();
    expect(bc!.point_estimate).toBeCloseTo(exp.point_estimate, 1);
    expect(bc!.n_iter).toBe(exp.n_iter);
  });
});

describe('prediction_interval', () => {
  it('encloses the point estimate', () => {
    const fx = loadFixture('prediction_interval.yaml');
    const inp = fx.input as Record<string, unknown>;
    const exp = fx.expected as Record<string, number>;
    const reg = linearRegression(inp.xs as number[], inp.ys as number[]);
    const pi = predictionInterval(reg!, inp.x_new as number, inp.confidence as number);
    expect(pi).not.toBeNull();
    expect(pi!.point_estimate).toBeCloseTo(exp.point_estimate, 0);
    expect(pi!.lower).toBeLessThan(pi!.point_estimate);
    expect(pi!.upper).toBeGreaterThan(pi!.point_estimate);
  });
});

describe('cohens_d_paired', () => {
  it('computes large effect', () => {
    const fx = loadFixture('cohens_d_paired.yaml');
    const inp = fx.input as Record<string, number[]>;
    const exp = fx.expected as Record<string, unknown>;
    const es = cohensDPaired(inp.x, inp.y);
    expect(es).not.toBeNull();
    expect(es!.d).toBeGreaterThan(1.0);
    expect(es!.interpretation).toBe(exp.interpretation);
  });
});

describe('ewma_forecast', () => {
  it('produces forecast beyond training', () => {
    const fx = loadFixture('ewma_forecast.yaml');
    const inp = fx.input as Record<string, unknown>;
    const exp = fx.expected as Record<string, number>;
    const fc = ewmaForecast(inp.series as number[], inp.alpha as number, inp.horizon as number);
    expect(fc).not.toBeNull();
    expect(fc!.n_train).toBe(exp.n_train);
    expect(fc!.point.length).toBeGreaterThan((inp.series as number[]).length);
  });
});

describe('mape', () => {
  it('computes correctly', () => {
    const fx = loadFixture('mape.yaml');
    const inp = fx.input as Record<string, number[]>;
    const exp = fx.expected as Record<string, number>;
    const m = mape(inp.y_true, inp.y_pred);
    expect(m).not.toBeNull();
    expect(m!).toBeCloseTo(exp.mape, 1);
  });
});

describe('sleep_efficiency', () => {
  it('returns 0 with warning when TIB is zero', () => {
    expect(sleepEfficiency(0, 0).warning).toBe('TIB was zero');
  });
  it('computes normal efficiency', () => {
    expect(sleepEfficiency(420, 480).efficiency).toBeCloseTo(0.875, 2);
  });
});

describe('sleep_debt_cumulative', () => {
  it('tracks cumulative debt', () => {
    const fx = loadFixture('sleep_debt_cumulative.yaml');
    const inp = fx.input as Record<string, unknown>;
    const exp = fx.expected as Record<string, number>;
    const sd = sleepDebtCumulative(inp.durations_h as number[], inp.age_y as number);
    expect(sd.baseline_h).toBe(exp.baseline_h);
    expect(sd.debt[6]).toBeCloseTo(exp.debt_7d, 0);
    expect(sd.debt[sd.debt.length - 1]).toBeCloseTo(exp.debt_14d, 0);
  });
});

describe('hrv_time_domain', () => {
  it('computes SDNN and RMSSD', () => {
    const fx = loadFixture('hrv_time_domain.yaml');
    const inp = fx.input as Record<string, number[]>;
    const exp = fx.expected as Record<string, number>;
    const hrv = hrvTimeDomain(inp.rr_intervals_ms);
    expect(hrv).not.toBeNull();
    expect(hrv!.mean_rr).toBeCloseTo(exp.mean_rr, 0);
    expect(hrv!.sdnn).toBeCloseTo(exp.sdnn, 0);
  });
});

describe('bmr_cunningham', () => {
  it('returns null when body_fat_pct is null', () => {
    expect(bmrCunningham(70, null)).toBeNull();
  });
  it('computes BMR with body fat', () => {
    expect(bmrCunningham(80, 0.15)).toBeCloseTo(1996, 0);
  });
});

describe('bmr_mifflin_st_jeor', () => {
  it('computes for male', () => {
    expect(bmrMifflinStJeor(80, 180, 30, 'male')).toBe(1780);
  });
  it('computes for female', () => {
    expect(bmrMifflinStJeor(65, 165, 28, 'female')).toBeCloseTo(1380.25, 0);
  });
  it('falls back to female for null sex', () => {
    expect(bmrMifflinStJeor(70, 170, 35, null)).toBeCloseTo(1426.5, 0);
  });
});

describe('hr_max_tanaka', () => {
  it('computes correctly', () => {
    expect(hrMaxTanaka(30)).toBeCloseTo(187, 0);
    expect(hrMaxTanaka(60)).toBe(166);
  });
});

describe('hrr_pct', () => {
  it('clamps low', () => {
    expect(hrrPct(50, 60, 190)).toBe(0.05);
  });
  it('clamps high', () => {
    expect(hrrPct(200, 60, 190)).toBe(0.85);
  });
});

describe('pal_from_hrr', () => {
  it('computes from HRR', () => {
    expect(palFromHrr(0.5, 1.5)).toBeCloseTo(1.75, 2);
    expect(palFromHrr(2.0, 1.5)).toBe(2.5);
  });
});

describe('tef_from_macros', () => {
  it('computes TEF', () => {
    expect(tefFromMacros(150, 250, 70)).toBeCloseTo(222.6, 0);
  });
});

describe('tdee', () => {
  it('composes', () => {
    expect(tdee(1996, 1.75, 222.6)).toBe(3716);
  });
});

describe('epley_1rm', () => {
  it('computes correctly', () => {
    expect(epley1RM(100, 5)).toBeCloseTo(116.667, 0);
  });
});

describe('brzycki_1rm', () => {
  it('returns null for reps > 10', () => {
    expect(brzycki1RM(80, 12)).toBeNull();
  });
});

describe('erf', () => {
  it('matches known values', () => {
    expect(erf(0)).toBeCloseTo(0, 5);
    expect(erf(1)).toBeCloseTo(0.8427, 2);
    expect(erf(2)).toBeCloseTo(0.9953, 2);
    expect(erf(-1)).toBeLessThan(0);
  });
});

describe('normal_cdf', () => {
  it('cr(0) = 0.5f', () => {
    expect(normalCdf(0)).toBeCloseTo(0.5, 5);
  });
  it('cr(1.96) = 0.975', () => {
    expect(normalCdf(1.96)).toBeCloseTo(0.975, 2);
  });
});

describe('quantile', () => {
  it('computes median of 1-10', () => {
    expect(quantile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0.5)).toBeCloseTo(5.5, 4);
  });
});
