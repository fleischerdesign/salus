import math


def mean(xs: list[float]) -> float | None:
    if not xs:
        return None
    return sum(xs) / len(xs)


def variance(xs: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    m = sum(xs) / n
    s2 = 0.0
    for x in xs:
        diff = x - m
        s2 += diff * diff
    return s2 / (n - 1)


def std(xs: list[float]) -> float | None:
    v = variance(xs)
    if v is None:
        return None
    return math.sqrt(v)


def covariance(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n != len(ys) or n < 2:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    s = 0.0
    for i in range(n):
        s += (xs[i] - mx) * (ys[i] - my)
    return s / (n - 1)


def quantile_rank(xs: list[float], x: float) -> float | None:
    if not xs:
        return None
    n = len(xs)
    count_lt = sum(1 for v in xs if v < x)
    count_eq = sum(1 for v in xs if v == x)
    if count_eq == 0:
        return count_lt / n
    return (count_lt + 0.5 * count_eq) / n


def rolling_mean(xs: list[float], window: int) -> list[float | None]:
    n = len(xs)
    result: list[float | None] = [None] * n
    if window < 1 or n < window:
        return result
    wsum = sum(xs[:window])
    result[window - 1] = wsum / window
    for i in range(window, n):
        wsum = wsum + xs[i] - xs[i - window]
        result[i] = wsum / window
    return result


def rolling_std(xs: list[float], window: int) -> list[float | None]:
    n = len(xs)
    result: list[float | None] = [None] * n
    if window < 2 or n < window:
        return result
    for i in range(window - 1, n):
        chunk = xs[i - window + 1 : i + 1]
        result[i] = std(chunk)
    return result


def rolling_zscore(xs: list[float], window: int) -> list[float | None]:
    n = len(xs)
    result: list[float | None] = [None] * n
    if window < 2 or n < window:
        return result
    r_mean = rolling_mean(xs, window)
    r_std = rolling_std(xs, window)
    for i in range(n):
        if r_mean[i] is not None and r_std[i] is not None and r_std[i] != 0:
            result[i] = (xs[i] - r_mean[i]) / r_std[i]  # type: ignore[operator]
    return result
