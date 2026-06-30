from datetime import datetime, timedelta
import json

from salus.models.analytics import WeightPoint, WeightTrend
from salus.repositories.measurement import MeasurementRepository


class WeightAnalysisService:
    def __init__(self, repo: MeasurementRepository) -> None:
        self._repo = repo

    def current(self) -> WeightPoint | None:
        rec = self._repo.find_latest("weight")
        if rec is None:
            return None
        d = json.loads(rec.value_json) if rec.value_json else {}
        return WeightPoint(
            date=rec.start_time.strftime("%Y-%m-%d"),
            weight_kg=d.get("kilograms", rec.value_numeric or 0),
        )

    def trend(self, days: int = 30) -> WeightTrend:
        since = datetime.today() - timedelta(days=days)
        records = self._repo.find_all(data_types=["weight"], since=since)
        seen: dict[str, float] = {}
        for rec in records:
            date = rec.start_time.strftime("%Y-%m-%d")
            if date not in seen:
                d = json.loads(rec.value_json) if rec.value_json else {}
                seen[date] = d.get("kilograms", rec.value_numeric or 0)
        points = sorted(
            [WeightPoint(date=d, weight_kg=w) for d, w in seen.items()],
            key=lambda p: p.date,
        )
        current = points[-1].weight_kg if points else None
        start = points[0].weight_kg if points else None
        delta = current - start if current is not None and start is not None else None
        return WeightTrend(points=points, current=current, start=start, delta=delta)
