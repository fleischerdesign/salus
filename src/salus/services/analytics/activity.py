from datetime import datetime, timedelta
import json

from salus.models.analytics import (
    ExerciseSession,
    HROHLC,
    HRSummary,
    HRTimelinePoint,
    StepDay,
)
from salus.repositories.protocols import IMeasurementRepository
from salus.services.analytics.calculations import map_exercise_type


class ActivityAnalysisService:
    def __init__(self, repo: IMeasurementRepository) -> None:
        self._repo = repo

    def steps_trend(
        self, days: int = 7, user_id: int | None = None, date: str | None = None
    ) -> list[StepDay]:
        anchor = (
            datetime.today() if date is None else datetime.strptime(date, "%Y-%m-%d")
        )

        # Query the entire range in a single database lookup
        start_date_str = (anchor - timedelta(days=days - 1)).strftime("%Y-%m-%d")
        since = datetime.fromisoformat(start_date_str + "T00:00:00")
        until = datetime.fromisoformat(anchor.strftime("%Y-%m-%d") + "T23:59:59")
        records = self._repo.find_all(
            data_types=["steps"], user_id=user_id, since=since, until=until
        )

        # Group records by date in memory
        by_date: dict[str, list] = {}
        for rec in records:
            d_str = rec.start_time.strftime("%Y-%m-%d")
            by_date.setdefault(d_str, []).append(rec)

        result: list[StepDay] = []
        for i in range(days):
            d = (anchor - timedelta(days=i)).strftime("%Y-%m-%d")
            day_records = by_date.get(d, [])
            count = 0
            for rec in day_records:
                if rec.value_numeric is not None:
                    c = int(rec.value_numeric)
                    if c > count:
                        count = c
            result.append(StepDay(date=d, count=count))
        result.sort(key=lambda s: s.date)
        return result

    def heart_rate_summary(
        self, user_id: int | None = None, date_str: str | None = None
    ) -> HRSummary | None:
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

    def heart_rate_timeline(
        self, user_id: int | None = None, date_str: str | None = None
    ) -> list[HRTimelinePoint]:
        if date_str is None:
            date_str = datetime.today().strftime("%Y-%m-%d")
        since = datetime.fromisoformat(date_str + "T00:00:00")
        until = datetime.fromisoformat(date_str + "T23:59:59")
        records = self._repo.find_all(
            data_types=["heart_rate"], user_id=user_id, since=since, until=until
        )
        points: list[HRTimelinePoint] = []
        for rec in reversed(records):
            if rec.value_numeric is not None and rec.value_numeric > 0:
                points.append(
                    HRTimelinePoint(
                        time=rec.start_time.strftime("%H:%M"),
                        bpm=float(rec.value_numeric),
                    )
                )
        return points

    _OHLC_DAY_LABELS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

    def heart_rate_ohlc(
        self, days: int = 7, user_id: int | None = None, date: str | None = None
    ) -> list[HROHLC]:
        if date is None:
            date = datetime.today().strftime("%Y-%m-%d")
        anchor = datetime.strptime(date, "%Y-%m-%d")

        # Query the entire range in a single database lookup
        start_date_str = (anchor - timedelta(days=days - 1)).strftime("%Y-%m-%d")
        since = datetime.fromisoformat(start_date_str + "T00:00:00")
        until = datetime.fromisoformat(anchor.strftime("%Y-%m-%d") + "T23:59:59")
        records = self._repo.find_all(
            data_types=["heart_rate"], user_id=user_id, since=since, until=until
        )

        # Group records by date in memory
        by_date: dict[str, list] = {}
        for rec in records:
            d_str = rec.start_time.strftime("%Y-%m-%d")
            by_date.setdefault(d_str, []).append(rec)

        result: list[HROHLC] = []
        for i in range(days - 1, -1, -1):
            d = anchor - timedelta(days=i)
            d_str = d.strftime("%Y-%m-%d")
            day_records = by_date.get(d_str, [])
            bpms = [
                float(r.value_numeric)
                for r in day_records
                if r.value_numeric is not None and r.value_numeric > 0
            ]
            if not bpms:
                result.append(
                    HROHLC(
                        date=d_str,
                        label=self._OHLC_DAY_LABELS[d.weekday()],
                        open_bpm=0,
                        high_bpm=0,
                        low_bpm=0,
                        close_bpm=0,
                        count=0,
                    )
                )
            else:
                result.append(
                    HROHLC(
                        date=d_str,
                        label=self._OHLC_DAY_LABELS[d.weekday()],
                        open_bpm=bpms[-1],
                        high_bpm=max(bpms),
                        low_bpm=min(bpms),
                        close_bpm=bpms[0],
                        count=len(bpms),
                    )
                )
        return result

    def exercise_history(
        self, days: int = 30, user_id: int | None = None, limit: int = 10
    ) -> list[ExerciseSession]:
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
