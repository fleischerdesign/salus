from typing import Callable

from salus.services.analytics.stats._dataclasses import BootstrapCI
from salus.services.analytics.stats._internal import quantile, xorshift64


def bootstrap_ci(
    xs: list[float],
    statistic: Callable[[list[float]], float],
    n_iter: int = 1000,
    seed: int = 42,
    confidence: float = 0.95,
) -> BootstrapCI | None:
    n = len(xs)
    if n < 2:
        return None
    point_est = statistic(xs)
    seed_state = seed
    stats: list[float] = []
    for _ in range(n_iter):
        sample = [xs[0]] * n
        for i in range(n):
            rnd, seed_state = xorshift64(seed_state)
            idx = int(rnd * n)
            sample[i] = xs[idx]
        stats.append(statistic(sample))
    tail = (1.0 - confidence) / 2.0
    lower = quantile(stats, tail)
    upper = quantile(stats, 1.0 - tail)
    if lower is None or upper is None:
        lower = point_est
        upper = point_est
    return BootstrapCI(
        lower=lower,
        upper=upper,
        point_estimate=point_est,
        n_iter=n_iter,
        confidence=confidence,
        seed=seed,
    )
