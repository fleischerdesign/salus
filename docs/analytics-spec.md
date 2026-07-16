# Salus Analysis Kernel — Algorithm Specification

**Version**: 1.0
**Status**: Contract (frozen)
**Principle**: The single source of truth is the algorithm, not the code line. Two
implementations — Python (`src/salus/services/analytics/stats/`) and TypeScript
(`frontend/src/lib/analytics/stats/`) — must produce numerically equivalent results,
verified by shared golden-value test vectors (`tests/fixtures/stats/*.yaml`).

## 1. Scope

This spec defines the pure-function statistical kernel consumed by:

- REST API `/api/v1/analytics/*` (server-side, authoritative on sync).
- Frontend analytics engine (client-side, offline-first, Dexie v8 cache).
- Cross-system consumers: `InsightService`, `GoalService`, `Workout` autoregulation
  and planner, `CircadianService`, `DashboardWidgetService`.

All functions are **pure, deterministic, zero-dependency** (no numpy / scipy / D3 in
the kernel). Iterative methods accept a `seed` parameter. Return types are frozen
dataclasses (Python) / readonly interfaces (TypeScript).

## 2. Conventions

| Convention | Rule |
|---|---|
| `confidence` | float in `(0, 1)`, default `0.95`. |
| `seed` | int or null; required by stochastic methods. Fixed seed ⇒ deterministic output. |
| `n` | reported on every returned struct where a sample size exists. |
| Numerical tolerance (golden tests) | `1e-6` relative for closed-form; `1e-3` for stochastic with fixed seed. |
| Citations | DOI when available; seminal paper otherwise. |
| Angles | degrees unless noted. |
| Null returns | functions return `None`/`null` for insufficient input (`n < 2`, zero variance); callers must guard. |

## 3. Kernel Primitives

### 3.1 `linear_regression(xs, ys) -> Regression`

OLS closed-form: `slope = cov(x,y) / var(x)`, `intercept = ȳ − slope·x̄`,
`r² = (Σ(xᵢ−x̄)(yᵢ−ȳ))² / (Σ(xᵢ−x̄)² · Σ(yᵢ−ȳ)²)`,
`SEE = sqrt(Σeᵢ² / df)`, `df = n − 2`.

```
Regression = { slope, intercept, r_squared, standard_error, n, residuals[], df }
```

**Reference**: Kutner, Nachtsheim, Neter, Li — *Applied Linear Statistical Models*,
5th ed., Ch. 1.
**Invariant**: `|r_squared| ≤ 1` (clamped for numerical drift). Returns null if
`n < 2` or zero variance in `xs`.

### 3.2 `prediction_interval(reg, x_new, confidence=0.95) -> PI`

`ŷ = intercept + slope·x_new`.
`PI = ŷ ± t_{α/2, df} · SEE · sqrt(1 + 1/n + (x_new − x̄)² / Σ(xᵢ−x̄)²)`.

t-distribution quantiles computed via the **incomplete-beta continued-fraction**
(Lentz 1976) — no hardcoded t-table. For `df > 30`, the t-quantile converges to z
and the incomplete-beta computation still drives it, so we use one path.

```
PI = { lower, upper, point_estimate, confidence }
```

**Reference**: Kutner §2.4.
**Invariant**: `lower ≤ point_estimate ≤ upper`. Returns null if `n < 3`.

### 3.3 `pearson(xs, ys) -> Correlation`

`r = Σ(xᵢ−x̄)(yᵢ−ȳ) / sqrt(Σ(xᵢ−x̄)² · Σ(yᵢ−ȳ)²)`.
`t = r · sqrt(df / (1 − r²))`. `p = 2 · (1 − T_cdf(|t|, df))` (incomplete beta).
Fisher-z CI: `z = atanh(r)`, `SE_z = 1 / sqrt(n − 3)`,
`CI_z = z ± z_{α/2} · SE_z`, back-transformed via `tanh`.

```
Correlation = { r, n, t_statistic, p_value, ci_lower, ci_upper, df }
```

**Reference**: Fisher 1915 (r-distribution); Fisher 1921 (z-transform).
**Invariant**: `|r| ≤ 1`; `0 ≤ p ≤ 1`; `CI` contains `r`.

### 3.4 `spearman(xs, ys) -> Correlation`

Pearson applied to rank-transformed values. Ties resolved via average rank. p-value
via the same t-approximation as Pearson on the ranked data.

**Reference**: Spearman 1904.

### 3.5 `cohens_d_paired(x, y) -> EffectSize`

`d = mean(x − y) / sd(x − y)` paired. Hedges' g small-sample correction for
`n < 20`: `g = d · (1 − 3 / (4n − 9))`. CI via noncentral-t approximation.
Interpretation (Cohen 1988): negligible `<0.2`, small `0.2–0.5`, medium `0.5–0.8`,
large `≥0.8`.

```
EffectSize = { d, hedges_g, ci_lower, ci_upper, n, interpretation }
```

**Reference**: Cohen 1988; Hedges 1981.

### 3.6 `benjamini_hochberg(p_values, alpha=0.05) -> FDR`

Sort p-values ascending. `adjusted[i] = p_sorted[i] · m / (i + 1)`, then enforce
monotonicity with a cumulative minimum from the largest down. `rejected[i] =
adjusted[i] ≤ alpha`. Returns in original input order.

```
FDR = { adjusted[], rejected[], alpha, method: "Benjamini-Hochberg FDR" }
```

**Reference**: Benjamini & Hochberg 1995, doi:10.1098/rstb.1995.0152.

### 3.7 `mann_kendall(series) -> TrendTest`

`S = Σ_{i<j} sign(x_j − x_i)`. Variance with tie correction:
`Var(S) = [n(n−1)(2n+5) − Σ t_k(t_k−1)(2t_k+5)] / 18`.
`Z = (S − 1)/sqrt(Var)` if `S > 0`, `(S + 1)/sqrt(Var)` if `S < 0`, else `0`.
`p = 2 · (1 − Φ(|Z|))` (normal CDF via erf approximation).
`tau = S / (n(n−1)/2)`.

```
TrendTest = { s, z, p_value, trend: "increasing"|"decreasing"|"none", n, tau }
```

**Reference**: Mann 1945; Kendall 1975.

### 3.8 `bootstrap_ci(xs, statistic, n_iter=1000, seed=42, confidence=0.95) -> BootstrapCI`

Resample `xs` with replacement `n_iter` times using a deterministic xorshift64 PRNG
seeded by `seed`. Apply `statistic` to each resample. Percentile method:
`lower = quantile(stats, (1−conf)/2)`, `upper = quantile(stats, 1 − (1−conf)/2)`,
via linear-interpolation quantile (Hyndman & Fan type 7).

```
BootstrapCI = { lower, upper, point_estimate, n_iter, confidence, seed }
```

**Reference**: Efron 1979; Efron & Tibshirani 1993, *An Introduction to the
Bootstrap*.
**Invariant**: fixed seed ⇒ deterministic. Returns null if `n < 2`.

### 3.9 `ewma_forecast(series, alpha=0.3, horizon=1) -> Forecast`

`ŷ_{t+1} = α·x_t + (1−α)·ŷ_t`, `ŷ_1 = x_1`. Residual-AR(1) correction:
`r̂_t = φ·r_{t−1}`, with `φ` via Yule-Walker on residuals. Final forecast
`ŷ_{T+h} = EWMA(T) + AR(1)·h`.

```
Forecast = { point[], fitted[], residuals[], mape, alpha, horizon, n_train }
```

**Reference**: Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*
Ch. 7 (online FPP3).
**Invariant**: `0 < alpha < 1`; `mape` returns null list-equivalent if any
`y_true = 0` (caller guards).

### 3.10 `mape(y_true, y_pred) -> number | null`

`mean(|（y_true − y_pred） / y_true|) · 100`. Returns null if any `y_true = 0`.

### 3.11 `resting_hr_windowed(readings, wake_ts, window_min=5) -> number | null`

Filter readings within `[wake_ts, wake_ts + 30·60]` (30 min post-wake). Sliding
`window_min`-minute moving average (centroid at midpoint). Return the minimum
moving-average value. Null if fewer than 2 readings in the window.

**Reference**: Brage et al. 2005, doi:10.1136/bjsm.2004.015456 — standardized
resting-HR protocol.
**Replaces**: current `resting_bpm = mean of lowest third` heuristic
(`services/analytics/activity.py:73`).

### 3.12 `sleep_efficiency(tst_min, tib_min) -> Efficiency`

`TST / TIB` as fraction `[0, 1]`. Warns if `tib_min = 0`.

**Reference**: AASM Scoring Manual v2.6, 2023.

### 3.13 `sleep_debt_cumulative(durations_h, age_y) -> { debt[], baseline_h }`

`baseline_h` from NSF age recommendations (Hirshkowitz 2015):
18–64 y → `8.0` (midpoint 7–9 h); ≥65 y → `7.5` (midpoint 7–8 h).
`debt[i] = Σ_{j≤i} (baseline_h − durations_h[j])`.

**Reference**: Hirshkowitz et al. 2015, doi:10.1016/j.sleep.2014.07.014.

### 3.14 `hrv_time_domain(rr_intervals_ms) -> HRV`

Standard AHA/EHRA/ACC definitions:
`SDNN = sqrt(Σ(rrᵢ − mean)² / (n − 1))`,
`RMSSD = sqrt(Σ(Δrrᵢ)² / n)`,
`pNN50 = count(|Δrr| > 50) / (n − 1)`.

```
HRV = { mean_rr, sdnn, rmssd, pnn50, n }
```

**Reference**: Sessa et al. 2018, doi:10.1093/eurheartj/ehy786 (AHA/EHRA/ACC
consensus on HRV).

### 3.15 Rolling statistics

`rolling_mean(xs, window)`, `rolling_std(xs, window)` (sample std, `ddof=1`),
`rolling_zscore(xs, window) = (x − rolling_mean) / rolling_std`. Output length `n`;
first `window − 1` entries are `null`. Welch's algorithm for numerical stability.

### 3.16 `quantile_rank(xs, x) -> number`

Linear-interpolation percentile rank (Hyndman & Fan 1996 type 7 — R default),
returns `(0, 1]`.
**Reference**: Hyndman & Fan 1996, doi:10.1080/01621459.1996.10476649.

### 3.17 `change_point_pelt(series, penalty="BIC") -> { indices[], costs[] }`

Pruned Exact Linear Time with mean-change segment cost (CUSUM). Penalty `BIC =
log(n) · σ²` (residual-variance estimate), `MBIC = log(n) + log(n − i)`.

**Reference**: Killick, Fearnhead, Eckley 2012, doi:10.1080/01621459.2012.718235.
Returns null if `n < 2`.

### 3.18 `rmssd_to_score(rmssd, mean_rmssd, std_rmssd) -> number`

Log transform `ln(rmssd)`, z-score against personal baseline, mapped to `0–100`
and clipped. Documented as **heuristic approximation** of consumer-app score
normalization; not endorsed by any vendor.

### 3.19 `bmr_cunningham(weight_kg, body_fat_pct=null) -> number | null`

If `body_fat_pct` in `[0, 1)`: `lbm = weight_kg · (1 − body_fat_pct)`,
`BMR = 500 + 22 · lbm`. Else returns null (caller falls back to Mifflin-St Jeor).

**Reference**: Cunningham 1991, doi:10.1093/ajcn/54.4.672.
**Replaces**: `calc_bmr_cunningham` in `calculations.py` which hardcodes
`age=30`/`height=181` in its fallback (incorrectly conflating Cunningham and
Mifflin-St Jeor).

### 3.20 `bmr_mifflin_st_jeor(weight_kg, height_cm, age_y, sex) -> number | null`

Males: `10·wt + 6.25·ht − 5·age + 5`.
Females: `10·wt + 6.25·ht − 5·age − 161`.
`sex = null`: conservative female fallback (simulates the lower metabolic end of
the Mifflin range). Caller should capture sex from the user profile.

**Reference**: Mifflin et al. 1990, doi:10.1093/ajcn/51.2.241.

### 3.21 `hr_max_tanaka(age_y) -> number`

`208 − 0.7 · age`.
**Reference**: Tanaka et al. 2001, doi:10.1161/01.CIR.96.2.220.

### 3.22 `hrr_pct(hr_avg_awake, hr_resting, hr_max) -> number`

`(hr_avg − hr_resting) / (hr_max − hr_resting)`, clamped to `[0.05, 0.85]`.
**Reference**: Brage 2005 (physiologically plausible HRR during waking activity).

### 3.23 `pal_from_hrr(hrr_pct, calibration_factor=1.5) -> number`

`PAL = max(1.0, min(2.5, 1.0 + hrr_pct · calibration_factor))`.
**Replaces**: inline calculation in `calc_tdee` (`calculations.py:111–115`).

### 3.24 `tef_from_macros(protein_g, carbs_g, fat_g) -> number`

`protein·4·0.25 + carbs·4·0.06 + fat·9·0.02`.
**Reference**: Reed & Hill 1996 (thermogenesis coefficients
0.25/0.06/0.02 of macros' gross kcal).

### 3.25 `tdee(bmr, pal, tef) -> number`

`round(bmr · pal + tef)`. Pure composition.

### 3.26 `epley_1rm(weight, reps) -> number`

`weight · (1 + reps / 30)`.
**Reference**: Epley 1985 (Poundage Chart, cited through Brzycki 1993).

### 3.27 `brzycki_1rm(weight, reps) -> number | null`

`weight · 36 / (37 − reps)`. Returns null if `reps > 10` (out of formula
validity — caller uses Epley).
**Reference**: Brzycki 1993, doi:10.1080/00140139308967886.

### 3.28 `one_rm_regression(sets, method="epley") -> 1RMResult`

Transform each set to estimated 1RM via the chosen formula. Take weighted mean by
volume, with `bootstrap_ci` (seeded) for the 95% CI.

```
1RMResult = { one_rm, ci_lower, ci_upper, n_sets, r_squared }
```

### 3.29 `tonnage_progression(sessions) -> Progression`

`linear_regression(week_index → tonnage)`; `mann_kendall` on the tonnage series;
`is_plateaued = mann_kendall.p_value > 0.05 AND r_squared < 0.2`.

```
Progression = { slope_kg_per_week, slope_ci[], r_squared, mann_kendall, is_plateaued }
```

### 3.30 `fatigue_emwa(daily_load, decay_positive=1/6, decay_negative=1/6) -> Fatigue`

Banister "Fitness-Fatigue" impulse model with separate positive/negative decays
(modern Clarke & Skiba formulation). `performance = fitness − fatigue`.

```
Fatigue = { fitness[], fatigue[], performance[] }
```

**Reference**: Banister 1975; Clarke & Skiba 2013, doi:10.2165/00007256-201333040-00002.

### 3.31 `recovery_composite(sleep_score, hrv_rmssd, resting_hr, steps, baselines) -> RecoveryScore`

z-scores vs. 28-day personal baselines:
`zSleep = (sleep_score − μSleep) / σSleep`,
`zHRV = (hrv_rmssd − μHRV) / σHRV`,
`zHR = −(resting_hr − μHR) / σHR` (negative — lower HR is better),
`zSteps = (log(steps) − μlogStep) / σlogStep`.
`score = 50 + 10 · (0.35·zSleep + 0.30·zHRV + 0.20·zHR + 0.15·zSteps)`,
clipped `[0, 100]`. Thresholds: `≥75 "primed"`, `50–75 "moderate"`,
`<50 "underrecovered"`.

**Reference / Limitations**: weights (0.35 / 0.30 / 0.20 / 0.15) are a documented
heuristic synthesised from Plews et al. 2013, doi:10.1152/japplphysiol.00770.2013.
No single authoritative weighting exists in the literature; this composition is
explicitly marked as a heuristic in the returned `methodology.note` field and is
not represented as an authoritative model.

## 4. Golden-Value Fixtures — Shared Protocol

Each fixture (`tests/fixtures/stats/*.yaml`) has this shape:

```yaml
name: <human-readable test name>
reference:
  citation: "<author, year, source>"
  doi: <string | null>
input:
  <arguments as named keys matching function signature>
expected:
  <returned struct fields with reference values>
tolerance:
  <per-field numerical tolerance>
```

Loaded by:
- `tests/test_stats_golden.py` (pytest parametrize) — runs Python implementation.
- `frontend/tests/stats-golden.test.ts` (vitest) — runs TS implementation.

CI asserts both pass and produce numerically equivalent results. A drift between
Python and TS is a CI failure.

## 5. Compliance Hard Gates

A function is kernel-compliant iff:

1. Pure — no side effects, deterministic unless `seed`-driven.
2. Zero external dependencies (stdlib math only).
3. Returns a frozen / readonly struct.
4. Has ≥ 1 golden-value fixture with a literature reference.
5. Passes both Python and TS golden tests (cross-language equivalence).
6. Reports `n` where applicable.
7. Reports p-value, effect size, CI for hypothesis tests.
8. Methodology block is composed by the **service layer** (kernel stays minimal);
   kernel structs do not carry `methodology` — the orchestrator composes that from
   the function names + a static `METHODS` registry keyed by primitive name.

## 6. Kernel-vs-Service Boundary

- **Kernel** (`services/analytics/stats/`): pure math primitives that could stand
  in for a `numpy`-style replacement. No DB, no IO, no caching, no Pydantic.
- **Service** (`services/analytics/`): DB access via injected repositories,
  caching (`data_version_token` ETag), response composition, `Methodology` assembly.

Composed primitives (`tdee`, `recovery_composite`) live in the kernel because they
benefit from a dedicated golden fixture and are reused by multiple consumers;
this keeps the orchestration layer free of cross-cutting math.

## 7. REST API Conformance

The `/api/v1/analytics/*` endpoints follow the existing project conventions
verbatim — no new patterns are introduced:

| Convention | Analytics applies |
|---|---|
| `APIRouter(prefix="/api/v1")` | identical to `api_dashboard.py`, `api_misc.py` |
| `current_user: User = Depends(get_current_user)` | identical |
| Service injection `Depends(get_analytics_service)` | factory exists at `dependencies.py:316` (currently dormant — revived) |
| Typed Pydantic `response_model=` | `schemas/analytics.py` (currently dormant — expanded) |
| Token auth + scopes | `get_current_user_or_api` (`dependencies.py:399`); reuses the existing `health:read` scope (`models/api_token.py:19` — already described as "Query health data (analytics/export)"). DRY — no scope explosion. |
| slowapi rate limiting | `main.py` already wires `SlowAPIMiddleware` and the `RateLimitExceeded` handler; expensive `/compute` endpoints decorate with `@limiter.limit`. |
| `Query(default=...)` / `Query(...)` | identical |
| Status codes 201/204, `ApiError` exceptions, JSON-only responses | identical |
| ETag / `If-None-Match` → 304 | new but follows the existing `X-Salus-Sync-Version` header convention style |

## 8. Versioning

- `X-Salus-Analytics-Version: 1` header on all `/api/v1/analytics/*` responses.
- Header supported (not yet rejected) inbound; preserves headroom for future algorithm
  migrations without breaking changes.

## 9. Internal Primitives

These building-block functions are kernel-internal; callers consume only the §3
public primitives, but both implementations must pass internal golden fixtures too
because correctness of §3 depends on them. Listed here for spec completeness.

### 9.1 `mean(xs) -> number`
Arithmetic mean. Returns null if `n = 0`.

### 9.2 `variance(xs) -> number`
Sample variance (`ddof=1`). Returns null if `n < 2`.

### 9.3 `std(xs) -> number`
`sqrt(variance(xs))`.

### 9.4 `covariance(xs, ys) -> number`
Sample covariance (`ddof=1`): `Σ(xᵢ−x̄)(yᵢ−ȳ) / (n−1)`. Returns null if `n < 2`.

### 9.5 `rank(xs) -> number[]`
Rank transform with average-rank tie resolution. Returns 1-indexed ranks in original
input order.

### 9.6 `quantile(xs, p) -> number`
Hyndman & Fan 1996 type 7 (R default) linear-interpolation quantile. `p ∈ (0, 1]`.
Returns null if `n = 0`.
**Reference**: Hyndman & Fan 1996, doi:10.1080/01621459.1996.10476649.

### 9.7 `erf(x) -> number`
Abramowitz & Stegun 7.1.26 rational-approximation of the error function.
Max absolute error ≤ `1.5e-7`.
**Reference**: Abramowitz & Stegun 1964, §7.1.26.

### 9.8 `normal_cdf(x, mu=0, sigma=1) -> number`
`Φ(x) = 0.5 · (1 + erf((x − mu) / (sigma · sqrt(2))))`.

### 9.9 `normal_ppf(p, mu=0, sigma=1) -> number`
Inverse normal CDF (probit) via the Acklam rational approximation (max relative
error ≤ `1.15e-9`).
**Reference**: Acklam 2004.

### 9.10 `incomplete_beta(a, b, x) -> number`
Regularised incomplete beta function `I_x(a, b)` via the continued-fraction method
of Lentz (max residual ≤ `1e-15`). Used by the t-distribution CDF:
`T_cdf(t, df) = 1 − 0.5 · I_{(df/(df+t²))}(df/2, 0.5)`.
**Reference**: Lentz 1976, Applied Optics, "Generating Bessel Functions by
Continued Fractions".

### 9.11 `t_cdf(t, df) -> number`
Student's t cumulative distribution via `incomplete_beta`.
`T_cdf(t, df) = 1 − 0.5 · I_{(df/(df+t²))}(df/2, 0.5)` for `t ≥ 0`; by symmetry
for `t < 0`: `T_cdf = 0.5 · I_{(df/(df+t²))}(df/2, 0.5)`.

### 9.12 `t_ppf(p, df) -> number`
Inverse t-CDF (t-quantile) via root-finding on `t_cdf` with bisection + Halley
refinement. For large df (>100), falls back to `normal_ppf`.

### 9.13 `xorshift64(state: { a: number }) -> { value: number, state }`
64-bit xorshift PRNG. State is the seed as a single integer. Returns `{ value: number
in [0, 1), state: updated seed }`. Deterministic; same seed ⇒ same sequence.
**Reference**: Marsaglia 2003, "Xorshift RNGs", Journal of Statistical Software,
doi:10.18637/jss.v008.i14.

### 9.14 `yule_walker_ar1(residuals) -> { phi, sigma2 }`
Autoregressive order-1 parameter estimation via Yule-Walker on a residuals series.
Returns null if `n < 2`. `phi = Σ(r_t·r_{t−1}) / Σ(r_t²)`, clipped to `[-0.99, 0.99]`.
Uses the phi to estimate `sigma2 = (1/n)·Σ(r_t − φ·r_{t−1})²`.

### 9.15 `gamma(n) -> number`
Gamma function `Γ(n)` via Lanczos approximation (g=7, p=9 coefficients). For
integer `n`, falls back to factorial.
**Reference**: Lanczos 1964, SIAM J. Num. Anal. B1.

### 9.16 `ln_gamma(x) -> number`
Log-gamma via Lanczos: avoids floating-point overflow for large arguments.

### 9.17 `beta(a, b) -> number`
`B(a,b) = exp(ln_gamma(a) + ln_gamma(b) − ln_gamma(a+b))`.

## 10. REST API Endpoints

All endpoints under `prefix="/api/v1"` with existing conventions.

### 10.1 `GET /api/v1/analytics/overview`

```
Parameters: range="30d"|"90d"|"1y", date=YYYY-MM-DD (default: today)
Auth: current_user OR api_token (scope: health:read)
Response: AnalyticsOverview {
  sleep: SleepSummary | null,
  weight_trend: WeightTrend | null,
  tdee: TDEEBlock | null,
  steps_trend: StepDay[],
  hr_summary: HRSummary | null,
  nutrition: NutritionDay[],
  exercise: ExerciseSession[],
  range_days: int,
  date: date
}
```

### 10.2 `GET /api/v1/analytics/timeseries`

```
Parameters: metric=string (metric_type source_data_type), range="30d"|"90d"|"1y",
            bucket="daily"|"weekly"|"monthly"
Auth: current_user OR api_token (scope: health:read)
Response: TimeSeries {
  metric: string,
  points: { date, value, ci_lower?, ci_upper? }[],
  regression?: Regression,
  forecast?: Forecast,
  n: int
}
Headers: X-Salus-Analytics-Version
Conditional: If-None-Match + ETag (via data_version_token)
```

### 10.3 `GET /api/v1/analytics/correlations`

```
Parameters: range="30d"|"90d"|"1y", min_n=14, methods="pearson,spearman"
Auth: current_user OR api_token (scope: health:read)
Response: CorrelationMatrix {
  pairs: [{ metric_a, metric_b, pearson_r, pearson_p, spearman_r, spearman_p,
            p_adjusted_BH, effect_size_d, ci_95_lower, ci_95_upper, n,
            interpretation_de, interpretation_en }],
  n_comparisons: int,
  correction: "Benjamini-Hochberg FDR",
  min_n: int,
  is_exploratory: true
}
```

### 10.4 `GET /api/v1/analytics/forecast`

```
Parameters: metric=string, horizon_days=30, method="linear"|"ewma"
Auth: current_user OR api_token (scope: health:read)
Response: ForecastResponse {
  metric: string,
  points: { date, predicted, ci_lower, ci_upper }[],
  method: string,
  r_squared: number,
  mape: number,
  n_train: int,
  horizon_days: int
}
```

### 10.5 `GET /api/v1/analytics/heatmap`

```
Parameters: metric=string, year=int
Auth: current_user OR api_token (scope: health:read)
Response: Heatmap {
  metric: string,
  year: int,
  days: { date, value, percentile_rank, is_null }[],
  max_value: number,
  method: "daily_max"|"daily_mean"|"daily_sum"
}
```

### 10.6 `GET /api/v1/analytics/methodology`

```
Auth: current_user OR api_token (scope: health:read)
Response: MethodologyIndex {
  methods: { name, description, doi?, citation, invariants[] }[]
}
```

### 10.7 `GET /api/v1/analytics/wellness-score`

```
Parameters: date=YYYY-MM-DD (default: today)
Auth: current_user OR api_token (scope: health:read)
Response: WellnessScore {
  date: date,
  score: 0..100,
  interpretation: "primed"|"moderate"|"underrecovered",
  components: { sleep, hrv, resting_hr, steps },
  baselines: { sleep_mean, hrv_mean, hr_mean, log_step_mean, stds },
  n_baseline_days: int
}
```

### 10.8 `GET /api/v1/analytics/workout/progression`

```
Parameters: exercise_id=string, range_days=180
Auth: current_user OR api_token (scope: health:read)
Response: WorkoutProgression {
  exercise: { id, name, equipment, primary_muscles },
  sessions: { date, total_tonnage, max_weight, sets_count }[],
  one_rm: 1RMResult,
  tonnage_progression: Progression,
  is_plateaued: boolean
}
```

### 10.9 `POST /api/v1/analytics/compute`

```
Body: AnalyticsComputeRequest {
  metric: string,
  range: "7d"|"30d"|"90d"|"1y",
  method: string,
  params: object?
}
Auth: current_user OR api_token (scope: health:read)
Rate limit: 5 req / min per token (expensive endpoint)
Response: AnalyticsComputeResponse {
  result: object,
  method: string,
  computation_time_ms: int,
  n: int
}
```

## 11. AnalyticsService Contract

`services/analytics/orchestrator.py` rewrite (currently unused). Replaces the
three parallel analytics code paths.

```
AnalyticsService(
    uow: IUnitOfWork,
    sleep_svc: SleepAnalysisService,
    activity_svc: ActivityAnalysisService,
    weight_svc: WeightAnalysisService,
    nutrition_svc: NutritionAnalysisService
)

async overview(user_id, range_key, date) -> AnalyticsOverview
async timeseries(user_id, metric, range_key, bucket) -> TimeSeries
async correlations(user_id, range_key, min_n, methods) -> CorrelationMatrix
async forecast(user_id, metric, horizon_days, method) -> ForecastResponse
async heatmap(user_id, metric, year) -> Heatmap
async wellness_score(user_id, date) -> WellnessScore
async workout_progression(user_id, exercise_id, range_days) -> WorkoutProgression
```

Each method:
1. Fetches raw measurements via injected repositories.
2. Calls kernel primitives (§3).
3. Composes `Methodology` sub-object from a static registry keyed by kernel
   function name (citation, doi, invariants, n).
4. Returns a Pydantic response model from `schemas/analytics.py`.
5. Computes `data_version_token = MAX(measurement.updated_at)` for ETag caching.

## 12. Shared Golden Fixtures — File Index

Every kernel primitive (§3 and §9) has one fixture file:

```
tests/fixtures/stats/
├── benjamini_hochberg.yaml
├── bmr_cunningham.yaml
├── bmr_mifflin_st_jeor.yaml
├── bootstrap_ci.yaml
├── brzycki_1rm.yaml
├── change_point_pelt.yaml
├── cohens_d_paired.yaml
├── epley_1rm.yaml
├── ewma_forecast.yaml
├── fatigue_emwa.yaml
├── hr_max_tanaka.yaml
├── hrr_pct.yaml
├── hrv_time_domain.yaml
├── linear_regression.yaml
├── mann_kendall.yaml
├── mape.yaml
├── one_rm_regression.yaml
├── pal_from_hrr.yaml
├── pearson.yaml
├── prediction_interval.yaml
├── recovery_composite.yaml
├── resting_hr_windowed.yaml
├── rmssd_to_score.yaml
├── sleep_debt_cumulative.yaml
├── sleep_efficiency.yaml
├── spearman.yaml
├── tdee.yaml
├── tef_from_macros.yaml
├── tonnage_progression.yaml
├── internal_erf.yaml
├── internal_incomplete_beta.yaml
├── internal_normal_cdf.yaml
├── internal_normal_ppf.yaml
├── internal_quantile.yaml
├── internal_rank.yaml
├── internal_stats.yaml
├── internal_t_cdf.yaml
├── internal_t_ppf.yaml
├── internal_xorshift64.yaml
├── internal_yule_walker.yaml
└── internal_l_gamma.yaml
```