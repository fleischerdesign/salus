"""Daily heatmap strategy (max value per day)."""
from datetime import datetime, timedelta, timezone

from salus.schemas.analytics import HeatmapDay, HeatmapResponse
from salus.services.analytics.strategies.context import AnalyticsContext


class HeatmapStrategy:
    def compute(
        self, ctx: AnalyticsContext, user_id: str, metric: str, year: int
    ) -> HeatmapResponse:
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        repo = ctx.uow.measurements
        records = repo.find_all(
            user_id=user_id, source_data_types=[metric], since=start, until=end
        )
        daily: dict[str, float] = {}
        for m in records:
            ds = m.start_time.strftime("%Y-%m-%d")
            daily[ds] = max(daily.get(ds, float("-inf")), m.value_numeric or 0.0)
        all_values = list(daily.values())
        max_val = max(all_values) if all_values else None
        n_vals = len(all_values)
        days_data: list[HeatmapDay] = []
        current = start.date()
        last = end.date()
        while current <= last:
            ds = current.isoformat()
            if ds in daily:
                v = daily[ds]
                rank = sum(1 for x in all_values if x < v) / max(n_vals, 1)
                days_data.append(
                    HeatmapDay(date=ds, value=v, percentile_rank=round(rank, 4))
                )
            else:
                days_data.append(HeatmapDay(date=ds, value=None, percentile_rank=None))
            current += timedelta(days=1)
        return HeatmapResponse(
            metric=metric,
            year=year,
            days=days_data,
            max_value=max_val,
            method="daily_max",
        )
