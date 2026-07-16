import math

from salus.services.analytics.stats._dataclasses import EfficiencyResult, HRV, RecoveryScore, SleepDebtResult


def resting_hr_windowed(
    readings: list[tuple[float, float]],
    wake_ts: float,
    window_min: float = 5.0,
) -> float | None:
    window_range = readings[:]
    window_sec = window_min * 60.0
    readings_in_window = [
        (t, bpm)
        for t, bpm in window_range
        if wake_ts <= t <= wake_ts + 30.0 * 60.0
    ]
    if len(readings_in_window) < 2:
        return None
    readings_in_window.sort(key=lambda r: r[0])
    n = len(readings_in_window)
    min_ma = float("inf")
    for start in range(n):
        window_vals = []
        mid = readings_in_window[start][0] + window_sec / 2.0
        for t, bpm in readings_in_window:
            if abs(t - mid) <= window_sec / 2.0:
                window_vals.append(bpm)
        if len(window_vals) >= 2:
            ma = sum(window_vals) / len(window_vals)
            if ma < min_ma:
                min_ma = ma
    return min_ma if min_ma != float("inf") else None


def sleep_efficiency(tst_min: float, tib_min: float) -> EfficiencyResult:
    if tib_min == 0.0:
        return EfficiencyResult(efficiency=0.0, warning="TIB was zero")
    return EfficiencyResult(
        efficiency=max(0.0, min(1.0, tst_min / tib_min)),
        warning=None,
    )


def sleep_debt_cumulative(durations_h: list[float], age_y: float) -> SleepDebtResult:
    if age_y >= 65:
        baseline_h = 7.5
    else:
        baseline_h = 8.0
    debt: list[float] = []
    cum = 0.0
    for d in durations_h:
        cum += baseline_h - d
        debt.append(cum)
    return SleepDebtResult(debt=tuple(debt), baseline_h=baseline_h)


def hrv_time_domain(rr_intervals_ms: list[float]) -> HRV | None:
    n = len(rr_intervals_ms)
    if n < 2:
        return None
    m = sum(rr_intervals_ms) / n
    sdnn = math.sqrt(sum((rr - m) ** 2 for rr in rr_intervals_ms) / (n - 1))
    diffs = [rr_intervals_ms[i] - rr_intervals_ms[i - 1] for i in range(1, n)]
    rmssd = math.sqrt(sum(d * d for d in diffs) / len(diffs))
    pnn50 = sum(1 for d in diffs if abs(d) > 50.0) / len(diffs)
    return HRV(mean_rr=m, sdnn=sdnn, rmssd=rmssd, pnn50=pnn50, n=n)


def rmssd_to_score(rmssd: float, mean_rmssd: float, std_rmssd: float) -> float:
    if std_rmssd == 0.0:
        return 50.0
    z = (math.log(max(rmssd, 1e-9)) - math.log(max(mean_rmssd, 1e-9))) / std_rmssd
    return max(0.0, min(100.0, 50.0 + 10.0 * z))


def recovery_composite(
    sleep_score: float,
    hrv_rmssd: float,
    resting_hr: float,
    steps: int,
    baselines: dict[str, tuple[float, float]],
    skip_steps: bool = False,
) -> RecoveryScore:
    mu_sleep, sig_sleep = baselines.get("sleep", (7.0, 1.0))
    mu_hrv, sig_hrv = baselines.get("hrv", (50.0, 10.0))
    mu_hr, sig_hr = baselines.get("resting_hr", (60.0, 5.0))
    mu_steps, sig_steps = baselines.get("log_steps", (8.0, 1.0))
    z_sleep = (sleep_score - mu_sleep) / max(sig_sleep, 1e-9)
    z_hrv = (hrv_rmssd - mu_hrv) / max(sig_hrv, 1e-9)
    z_hr = -(resting_hr - mu_hr) / max(sig_hr, 1e-9)
    z_steps = 0.0 if skip_steps else (math.log(max(steps, 1)) - mu_steps) / max(sig_steps, 1e-9)
    score = 50.0 + 10.0 * (0.35 * z_sleep + 0.30 * z_hrv + 0.20 * z_hr + 0.15 * z_steps)
    score = max(0.0, min(100.0, score))
    if score >= 75:
        interp = "primed"
    elif score >= 50:
        interp = "moderate"
    else:
        interp = "underrecovered"
    return RecoveryScore(
        score=score,
        interpretation=interp,
        sleep_z=z_sleep,
        hrv_z=z_hrv,
        hr_z=z_hr,
        steps_z=z_steps,
    )
