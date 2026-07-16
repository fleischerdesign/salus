import math

from salus.services.analytics.stats._dataclasses import Fatigue, OneRMResult, Progression, TrendTest
from salus.services.analytics.stats._bootstrap import bootstrap_ci
from salus.services.analytics.stats._multiple import mann_kendall
from salus.services.analytics.stats._regression import linear_regression
from salus.services.analytics.stats._stats import mean


def epley_1rm(weight: float, reps: float) -> float:
    return weight * (1.0 + reps / 30.0)


def brzycki_1rm(weight: float, reps: float) -> float | None:
    if reps > 10:
        return None
    return weight * 36.0 / (37.0 - reps)


def one_rm_regression(
    sets: list[tuple[float, float]], method: str = "epley"
) -> OneRMResult | None:
    if len(sets) < 1:
        return None
    transformer = epley_1rm if method == "epley" else brzycki_1rm
    estimates: list[float] = []
    for weight, reps in sets:
        est = transformer(weight, reps)
        if est is not None:
            estimates.append(est)
    if not estimates:
        return None
    one_rm = sum(estimates) / len(estimates)
    if len(estimates) >= 3:
        bc = bootstrap_ci(estimates, lambda xs: mean(xs) or 0.0, n_iter=500, seed=42)
        ci_lower = bc.lower if bc else one_rm
        ci_upper = bc.upper if bc else one_rm
    else:
        ci_lower = one_rm
        ci_upper = one_rm
    xs = list(range(len(estimates)))
    reg = linear_regression([float(x) for x in xs], estimates)
    r_sq = reg.r_squared if reg else 0.0
    return OneRMResult(
        one_rm=one_rm,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        n_sets=len(sets),
        r_squared=r_sq,
    )


def tonnage_progression(
    sessions: list[tuple[int, float]],
) -> Progression | None:
    if len(sessions) < 2:
        return None
    weeks: list[float] = []
    tonnages: list[float] = []
    for w, t in sessions:
        weeks.append(float(w))
        tonnages.append(t)
    reg = linear_regression(weeks, tonnages)
    if reg is None:
        return None
    mk = mann_kendall(tonnages)
    is_plateaued = False
    if mk is not None:
        is_plateaued = mk.p_value > 0.05 and reg.r_squared < 0.2
    se = reg.standard_error
    ci_margin = 1.96 * se / math.sqrt(max(reg.n, 1))
    return Progression(
        slope_kg_per_week=reg.slope,
        slope_ci=(reg.slope - ci_margin, reg.slope + ci_margin),
        r_squared=reg.r_squared,
        mann_kendall=mk or TrendTest(s=0.0, z=0.0, p_value=1.0, trend="none", n=0, tau=0.0),
        is_plateaued=is_plateaued,
    )


def fatigue_emwa(
    daily_load: list[float],
    decay_positive: float = 1.0 / 6.0,
    decay_negative: float = 1.0 / 6.0,
) -> Fatigue | None:
    n = len(daily_load)
    if n == 0:
        return None
    fitness = [0.0] * n
    fatigue = [0.0] * n
    performance = [0.0] * n
    for i in range(n):
        if i == 0:
            fitness[i] = daily_load[i] * decay_positive
            fatigue[i] = daily_load[i] * decay_negative
        else:
            fitness[i] = daily_load[i] * decay_positive + fitness[i - 1] * (1.0 - decay_positive)
            fatigue[i] = daily_load[i] * decay_negative + fatigue[i - 1] * (1.0 - decay_negative)
        performance[i] = fitness[i] - fatigue[i]
    return Fatigue(
        fitness=tuple(fitness),
        fatigue=tuple(fatigue),
        performance=tuple(performance),
    )
