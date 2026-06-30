from datetime import datetime, timedelta

from salus.models.analytics import SleepSummary
from salus.repositories.measurement import MeasurementRepository
from salus.services.analytics.calculations import map_sleep_stage


class SleepAnalysisService:
    def __init__(self, repo: MeasurementRepository) -> None:
        self._repo = repo

    def last_night(self) -> SleepSummary | None:
        today = datetime.today()
        since = today.replace(hour=0, minute=0, second=0, microsecond=0)
        until = today.replace(hour=23, minute=59, second=59, microsecond=0)
        records = self._repo.find_all(
            data_types=["sleep"], since=since, until=until, limit=1
        )
        if not records:
            return None
        return self._build_summary(records[0])

    def trend(self, days: int = 7) -> list[SleepSummary]:
        since = datetime.today() - timedelta(days=days)
        records = self._repo.find_all(data_types=["sleep"], since=since)
        summaries: list[SleepSummary] = []
        seen_dates: set[str] = set()
        for rec in records:
            date = rec.start_time.strftime("%Y-%m-%d")
            if date in seen_dates:
                continue
            seen_dates.add(date)
            summaries.append(self._build_summary(rec))
        summaries.sort(key=lambda s: s.date)
        return summaries

    def _build_summary(self, record) -> SleepSummary:
        import json
        data = json.loads(record.value_json) if record.value_json else {}
        duration = data.get("duration_seconds", 0)
        stages = data.get("stages", [])
        stage_totals: dict[str, int] = {}
        for s in stages:
            sn = str(s.get("stage", ""))
            name = map_sleep_stage(sn)
            stage_totals[name] = stage_totals.get(name, 0) + s.get(
                "duration_seconds", 0
            )
        return SleepSummary(
            date=record.start_time.strftime("%Y-%m-%d"),
            duration_seconds=duration,
            duration_hours=duration / 3600 if duration else 0,
            awake_seconds=stage_totals.get("Awake", 0),
            light_seconds=stage_totals.get("Light", 0),
            deep_seconds=stage_totals.get("Deep", 0),
            rem_seconds=stage_totals.get("REM", 0),
        )
