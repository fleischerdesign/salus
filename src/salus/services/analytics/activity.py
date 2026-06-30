from datetime import datetime, timedelta
import json

from salus.models.analytics import ExerciseSession, HRSummary, StepDay
from salus.repositories.measurement import MeasurementRepository
from salus.services.analytics.calculations import (
    map_exercise_type,
    samsung_day_boundary,
)


class ActivityAnalysisService:
    def __init__(self, repo: MeasurementRepository) -> None:
        self._repo = repo

    def steps_trend(self, days: int = 7, user_id: int | None = None, date: str | None = None) -> list[StepDay]:
        result: list[StepDay] = []
        anchor = datetime.today() if date is None else datetime.strptime(date, "%Y-%m-%d")
        for i in range(days):
            d = (anchor - timedelta(days=i)).strftime("%Y-%m-%d")
            day_start, day_end = samsung_day_boundary(d)
            records = self._repo.find_all(data_types=["steps"], user_id=user_id)
            count = 0
            for rec in records:
                if rec.end_time and day_start <= rec.end_time.strftime("%Y-%m-%dT%H:%M:%S") < day_end:
                    if rec.value_numeric is not None:
                        c = int(rec.value_numeric)
                        if c > count:
                            count = c
            result.append(StepDay(date=d, count=count))
        result.sort(key=lambda s: s.date)
        return result

    def heart_rate_summary(self, user_id: int | None = None, date_str: str | None = None) -> HRSummary | None:
        if date_str is None:
            date_str = datetime.today().strftime("%Y-%m-%d")
        since = datetime.fromisoformat(date_str + "T00:00:00")
        until = datetime.fromisoformat(date_str + "T23:59:59")
        records = self._repo.find_all(
            data_types=["heart_rate"], user_id=user_id, since=since, until=until
        )
        bpms: list[float] = []
        for rec in records:
            if rec.value_numeric is not None and rec.value_numeric > 0:
                bpms.append(float(rec.value_numeric))
        if not bpms:
            return None
        avg = sum(bpms) / len(bpms)
        sorted_bpms = sorted(bpms)
        resting = sum(sorted_bpms[: max(1, len(bpms) // 3)]) / max(1, len(bpms) // 3)
        return HRSummary(
            date=date_str,
            measurement_count=len(bpms),
            avg_bpm=round(avg, 1),
            resting_bpm=round(resting, 1),
            min_bpm=int(min(bpms)),
            max_bpm=int(max(bpms)),
        )

    def exercise_history(self, days: int = 30, user_id: int | None = None, limit: int = 10) -> list[ExerciseSession]:
        since = datetime.today() - timedelta(days=days)
        records = self._repo.find_all(
            data_types=["exercise"], user_id=user_id, since=since, limit=limit
        )
        sessions: list[ExerciseSession] = []
        for rec in records:
            d = json.loads(rec.value_json) if rec.value_json else {}
            ex_type = d.get("exercise_type", d.get("type", 0))
            try:
                ex_type = int(ex_type)
            except (ValueError, TypeError):
                ex_type = 0
            sessions.append(
                ExerciseSession(
                    date=rec.start_time.strftime("%Y-%m-%d"),
                    time=rec.start_time.strftime("%H:%M"),
                    type_name=map_exercise_type(ex_type),
                    duration_seconds=d.get("duration_seconds", 0),
                    distance_meters=d.get("distance_meters", 0),
                    calories=d.get("calories", 0),
                )
            )
        return sessions
