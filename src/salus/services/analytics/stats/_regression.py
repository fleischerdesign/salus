import math

from salus.services.analytics.stats._dataclasses import PI, Regression
from salus.services.analytics.stats._internal import t_ppf
from salus.services.analytics.stats._stats import covariance, std


def linear_regression(xs: list[float], ys: list[float]) -> Regression | None:
    n = len(xs)
    if n != len(ys) or n < 2:
        return None
    x_std = std(xs)
    if x_std is None or x_std == 0.0:
        return None
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    cov_val = covariance(xs, ys)
    if cov_val is None:
        return None
    slope = cov_val / (x_std * x_std)
    intercept = y_mean - slope * x_mean
    residuals = tuple(ys[i] - (intercept + slope * xs[i]) for i in range(n))
    df = n - 2
    sse = sum(e * e for e in residuals)
    see = math.sqrt(sse / df) if df > 0 else 0.0
    y_var = sum((y - y_mean) ** 2 for y in ys)
    r_squared = max(0.0, min(1.0, 1.0 - sse / y_var if y_var > 0 else 0.0))
    ssx = (x_std * x_std) * (n - 1)
    return Regression(
        slope=slope,
        intercept=intercept,
        r_squared=r_squared,
        standard_error=see,
        n=n,
        residuals=residuals,
        df=df,
        x_mean=x_mean,
        ssx=ssx,
    )


def prediction_interval(
    reg: Regression,
    x_new: float,
    confidence: float = 0.95,
) -> PI | None:
    if reg.n < 3:
        return None
    pe = reg.intercept + reg.slope * x_new
    alpha = 1.0 - confidence
    t_crit = t_ppf(1.0 - alpha / 2.0, float(reg.df)) if reg.df > 0 else 1.96
    se_pred = reg.standard_error * math.sqrt(1.0 + 1.0 / reg.n + (x_new - reg.x_mean) ** 2 / max(reg.ssx, 1e-12))
    margin = t_crit * se_pred
    return PI(
        lower=pe - margin,
        upper=pe + margin,
        point_estimate=pe,
        confidence=confidence,
    )
