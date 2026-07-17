from datetime import datetime, timedelta

from salus.models.analytics import BloodPressurePoint
from salus.repositories.protocols import IMeasurementRepository


class BloodPressureAnalysisService:
    def __init__(self, repo: IMeasurementRepository) -> None:
        self._repo = repo

    def trend(
        self, days: int = 30, user_id: str | None = None
    ) -> list[BloodPressurePoint]:
        since = datetime.today() - timedelta(days=days)
        systolic = self._repo.find_by_metric_type("systolic_bp", user_id=user_id)
        diastolic = self._repo.find_by_metric_type("diastolic_bp", user_id=user_id)

        by_date: dict[str, dict[str, list[float]]] = {}
        for m in systolic:
            if m.start_time < since:
                continue
            date_str = m.start_time.strftime("%Y-%m-%d")
            if date_str not in by_date:
                by_date[date_str] = {"systolic": [], "diastolic": []}
            if m.value_numeric is not None:
                by_date[date_str]["systolic"].append(m.value_numeric)

        for m in diastolic:
            if m.start_time < since:
                continue
            date_str = m.start_time.strftime("%Y-%m-%d")
            if date_str not in by_date:
                by_date[date_str] = {"systolic": [], "diastolic": []}
            if m.value_numeric is not None:
                by_date[date_str]["diastolic"].append(m.value_numeric)

        points: list[BloodPressurePoint] = []
        for date_str in sorted(by_date.keys()):
            d = by_date[date_str]
            sys_vals = d["systolic"]
            dia_vals = d["diastolic"]
            if sys_vals and dia_vals:
                points.append(
                    BloodPressurePoint(
                        date=date_str,
                        systolic=sum(sys_vals) / len(sys_vals),
                        diastolic=sum(dia_vals) / len(dia_vals),
                    )
                )

        return points
