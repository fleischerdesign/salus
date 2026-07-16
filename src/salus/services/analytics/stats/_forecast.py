from salus.services.analytics.stats._dataclasses import Forecast
from salus.services.analytics.stats._internal import yule_walker_ar1


def ewma_forecast(
    series: list[float],
    alpha: float = 0.3,
    horizon: int = 1,
) -> Forecast | None:
    n = len(series)
    if n < 2 or not (0.0 < alpha < 1.0):
        return None
    fitted = [series[0]]
    for i in range(1, n):
        fitted.append(alpha * series[i - 1] + (1.0 - alpha) * fitted[i - 1])
    residuals = [series[i] - fitted[i] for i in range(n)]
    residuals_short = residuals[1:]
    yw = yule_walker_ar1(residuals_short)
    phi = 0.0
    if yw is not None:
        phi, _sigma2 = yw
    point = list(series)
    for h in range(1, horizon + 1):
        fw = alpha * series[n - 1] + (1.0 - alpha) * fitted[n - 1]
        fw += phi * residuals[n - 1]
        point.append(fw)
    mape_val = mape(series[1:], fitted[1:])
    return Forecast(
        point=tuple(point),
        fitted=tuple(fitted),
        residuals=tuple(residuals),
        mape=mape_val,
        alpha=alpha,
        horizon=horizon,
        n_train=n,
    )


def mape(y_true: list[float], y_pred: list[float]) -> float | None:
    n = len(y_true)
    if n != len(y_pred) or n == 0:
        return None
    for y in y_true:
        if y == 0.0:
            return None
    abs_pct = [abs((y_true[i] - y_pred[i]) / y_true[i]) for i in range(n)]
    return sum(abs_pct) / n * 100.0
