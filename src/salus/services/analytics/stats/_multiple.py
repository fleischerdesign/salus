import math

from salus.services.analytics.stats._dataclasses import FDR, TrendTest
from salus.services.analytics.stats._internal import normal_cdf


def benjamini_hochberg(p_values: list[float], alpha: float = 0.05) -> FDR:
    m = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda kv: kv[1])
    adj_sorted = [min(p * m / (i + 1), 1.0) for i, (_, p) in enumerate(indexed)]
    for i in range(m - 2, -1, -1):
        adj_sorted[i] = min(adj_sorted[i], adj_sorted[i + 1])
    adjusted = [0.0] * m
    rejected = [False] * m
    for rank, (orig_idx, _) in enumerate(indexed):
        adjusted[orig_idx] = adj_sorted[rank]
        rejected[orig_idx] = adj_sorted[rank] <= alpha
    return FDR(adjusted=tuple(adjusted), rejected=tuple(rejected), alpha=alpha)


def mann_kendall(series: list[float]) -> TrendTest | None:
    n = len(series)
    if n < 3:
        return None
    s = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            diff = series[j] - series[i]
            if diff > 0:
                s += 1.0
            elif diff < 0:
                s -= 1.0
    counts: dict[float, int] = {}
    for v in series:
        counts[v] = counts.get(v, 0) + 1
    tie_correction = 0.0
    for t in counts.values():
        if t > 1:
            tie_correction += t * (t - 1) * (2 * t + 5)
    var_s = (n * (n - 1) * (2 * n + 5) - tie_correction) / 18.0
    var_s = max(var_s, 1e-12)
    if s > 0:
        z = (s - 1.0) / math.sqrt(var_s)
    elif s < 0:
        z = (s + 1.0) / math.sqrt(var_s)
    else:
        z = 0.0
    p_val = 2.0 * (1.0 - normal_cdf(abs(z)))
    tau = s / (n * (n - 1) / 2.0)
    if p_val < 0.05 and z > 0:
        trend = "increasing"
    elif p_val < 0.05 and z < 0:
        trend = "decreasing"
    else:
        trend = "none"
    return TrendTest(s=s, z=z, p_value=p_val, trend=trend, n=n, tau=tau)
