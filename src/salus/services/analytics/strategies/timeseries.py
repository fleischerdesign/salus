"""Time-series bucketing strategy."""
from datetime import datetime, timedelta, timezone

from salus.schemas.analytics import TimeSeriesPoint, TimeSeriesResponse
from salus.services.analytics.strategies._helpers import metrics_require_sum
from salus.services.analytics.strategies.context import AnalyticsContext

RANGE_DAYS: dict[str, int] = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}


class TimeseriesStrategy:
    def compute(
        self,
        ctx: AnalyticsContext,
        user_id: str,
        metric: str,
        range_key: str = "30d",
        bucket: str = "daily",
    ) -> TimeSeriesResponse:
        days = RANGE_DAYS.get(range_key, 30)
        since = datetime.now(timezone.utc) - timedelta(days=days)
        repo = ctx.uow.measurements
        records = repo.find_all(
            user_id=user_id, source_data_types=[metric], since=since
        )
        records.sort(key=lambda m: m.start_time)
        bucket_values: dict[str, list[float]] = {}
        for m in records:
            key = m.start_time.strftime("%Y-%m-%d")
            if bucket == "weekly":
                iso = m.start_time.isocalendar()
                key = f"{iso[0]}-W{iso[1]:02d}"
            elif bucket == "monthly":
                key = m.start_time.strftime("%Y-%m")
            if key not in bucket_values:
                bucket_values[key] = []
            bucket_values[key].append(
                m.value_numeric if m.value_numeric is not None else 0.0
            )
        aggregated: list[tuple[str, float]] = []
        for k, vals in sorted(bucket_values.items()):
            if metrics_require_sum(metric):
                aggregated.append((k, sum(vals)))
            else:
                aggregated.append((k, sum(vals) / len(vals)))
        ts_points = [TimeSeriesPoint(date=d, value=v) for d, v in aggregated]
        return TimeSeriesResponse(
            metric=metric,
            points=ts_points,
            n=len(ts_points),
            bucket=bucket,
            range_key=range_key,
        )
