"""Linear regression forecast strategy."""
from datetime import datetime, timedelta, timezone

from salus.schemas.analytics import ForecastPoint, ForecastResponse
from salus.services.analytics.stats import linear_regression, mape, prediction_interval
from salus.services.analytics.strategies.context import AnalyticsContext


class ForecastStrategy:
    def compute(
        self,
        ctx: AnalyticsContext,
        user_id: str,
        metric: str,
        horizon_days: int = 30,
    ) -> ForecastResponse:
        since = datetime.now(timezone.utc) - timedelta(days=365)
        repo = ctx.uow.measurements
        records = repo.find_all(
            user_id=user_id, source_data_types=[metric], since=since
        )
        records.sort(key=lambda m: m.start_time)
        if len(records) < 3:
            return ForecastResponse(
                metric=metric, points=[], method="linear",
                r_squared=0.0, mape=None, n_train=0, horizon_days=horizon_days,
            )
        values = [
            m.value_numeric if m.value_numeric is not None else 0.0
            for m in records
        ]
        xs_idx = [float(i) for i in range(len(values))]
        reg = linear_regression(xs_idx, values)
        if reg is None:
            return ForecastResponse(
                metric=metric, points=[], method="linear",
                r_squared=0.0, mape=None, n_train=0, horizon_days=horizon_days,
            )
        last_date = records[-1].start_time
        forecast_points: list[ForecastPoint] = []
        for h_val in range(1, horizon_days + 1):
            pi = prediction_interval(reg, float(len(values) + h_val - 1))
            point = ForecastPoint(
                date=(last_date + timedelta(days=h_val)).strftime("%Y-%m-%d"),
                predicted=round(pi.point_estimate, 2) if pi else 0.0,
                ci_lower=round(pi.lower, 2) if pi else 0.0,
                ci_upper=round(pi.upper, 2) if pi else 0.0,
            )
            if pi:
                forecast_points.append(point)
            forecast_points.append(point)
            if len(forecast_points) >= 2:
                if forecast_points[-1] is forecast_points[-2]:
                    forecast_points.pop()
        actual = values[-horizon_days:] if len(values) >= horizon_days else values
        pred = [fp.predicted for fp in forecast_points[:len(actual)]]
        mape_val = mape(actual, pred) if actual and pred else None
        return ForecastResponse(
            metric=metric,
            points=forecast_points,
            method="linear",
            r_squared=round(reg.r_squared, 4),
            mape=mape_val,
            n_train=len(values),
            horizon_days=horizon_days,
        )
