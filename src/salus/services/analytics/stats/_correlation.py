import math

from salus.services.analytics.stats._dataclasses import Correlation, EffectSize
from salus.services.analytics.stats._internal import incomplete_beta, rank
from salus.services.analytics.stats._stats import std


def pearson(xs: list[float], ys: list[float]) -> Correlation | None:
    n = len(xs)
    if n != len(ys) or n < 3:
        return None
    x_std = std(xs)
    y_std = std(ys)
    if x_std is None or y_std is None or x_std == 0.0 or y_std == 0.0:
        return None
    m_x = sum(xs) / n
    m_y = sum(ys) / n
    num = sum((xs[i] - m_x) * (ys[i] - m_y) for i in range(n))
    den = math.sqrt(sum((x - m_x) ** 2 for x in xs) * sum((y - m_y) ** 2 for y in ys))
    if den == 0.0:
        return None
    r = max(-1.0, min(1.0, num / den))
    df = n - 2
    if abs(r) >= 1.0 - 1e-15:
        t_stat = float("inf") if r >= 0 else float("-inf")
        p_val = 0.0
    else:
        t_stat = r * math.sqrt(df / (1.0 - r * r))
        x_beta = df / (df + t_stat * t_stat)
        ib = incomplete_beta(df / 2.0, 0.5, x_beta)
        p_val = ib if t_stat >= 0 else 2.0 - ib
        p_val = max(0.0, min(1.0, p_val))
    z_fisher = math.atanh(r) if abs(r) < 1.0 else math.copysign(float("inf"), r)
    se_z = 1.0 / math.sqrt(n - 3)
    z_alpha = _z_critical(0.95)
    ci_lower = math.tanh(z_fisher - z_alpha * se_z)
    ci_upper = math.tanh(z_fisher + z_alpha * se_z)
    return Correlation(
        r=r,
        n=n,
        t_statistic=t_stat,
        p_value=p_val,
        ci_lower=max(-1.0, min(1.0, ci_lower)),
        ci_upper=max(-1.0, min(1.0, ci_upper)),
        df=df,
    )


def spearman(xs: list[float], ys: list[float]) -> Correlation:
    rx = rank(list(xs))
    ry = rank(list(ys))
    return pearson(rx, ry)  # type: ignore[return-value]


def cohens_d_paired(x: list[float], y: list[float]) -> EffectSize | None:
    n = len(x)
    if n != len(y) or n < 2:
        return None
    diffs = [x[i] - y[i] for i in range(n)]
    d_mean = sum(diffs) / n
    d_sd = 0.0
    for d in diffs:
        d_sd += (d - d_mean) ** 2
    d_sd = math.sqrt(d_sd / (n - 1)) if n > 1 else 0.0
    if d_sd == 0.0:
        return EffectSize(
            d=0.0,
            hedges_g=0.0,
            ci_lower=0.0,
            ci_upper=0.0,
            n=n,
            interpretation="negligible",
        )
    d_val = d_mean / d_sd
    hedges_g = d_val
    if n < 20:
        hedges_g = d_val * (1.0 - 3.0 / (4.0 * n - 9.0))
    se_d = math.sqrt(1.0 / n + d_val * d_val / (2.0 * n))
    z_crit = _z_critical(0.95)
    ci_lower = d_val - z_crit * se_d
    ci_upper = d_val + z_crit * se_d
    abs_d = abs(d_val)
    if abs_d >= 0.8:
        interp = "large"
    elif abs_d >= 0.5:
        interp = "medium"
    elif abs_d >= 0.2:
        interp = "small"
    else:
        interp = "negligible"
    return EffectSize(
        d=d_val,
        hedges_g=hedges_g,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        n=n,
        interpretation=interp,
    )


def _z_critical(confidence: float) -> float:
    z_map = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    return z_map.get(confidence, 1.96)
