"""Scheduled data-quality jobs (run by ``services.scheduler.AppScheduler``)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlmodel import col, select

from salus.models.data_quality import DataQualityFlag
from salus.models.measurement import Measurement
from salus.services.data_quality.service import DataQualityService

FLAG_RETENTION_DAYS = 180


class DataQualityRecheckJob:
    name = "data_quality_recheck"
    interval_seconds = 6 * 3600

    def __init__(self, interval_seconds: int | None = None) -> None:
        if interval_seconds is not None:
            self.interval_seconds = interval_seconds

    def run(self, session_factory) -> None:
        from salus.repositories.unit_of_work import SqlUnitOfWork

        with session_factory() as session:
            cutoff = datetime.now(timezone.utc) - timedelta(days=1)
            user_ids = session.exec(
                select(Measurement.user_id).where(
                    Measurement.created_at >= cutoff,
                    col(Measurement.user_id).is_not(None),
                ).distinct()
            ).all()
            service = DataQualityService(SqlUnitOfWork(session))
            for user_id in user_ids:
                if user_id:
                    service.run_checks(user_id)
            session.commit()


class DataQualityCleanupJob:
    name = "data_quality_cleanup"
    interval_seconds = 24 * 3600

    def __init__(self, interval_seconds: int | None = None) -> None:
        if interval_seconds is not None:
            self.interval_seconds = interval_seconds

    def run(self, session_factory) -> None:
        with session_factory() as session:
            cutoff = datetime.now(timezone.utc) - timedelta(days=FLAG_RETENTION_DAYS)
            stale = session.exec(
                select(DataQualityFlag).where(DataQualityFlag.created_at < cutoff)
            ).all()
            for flag in stale:
                session.delete(flag)
            session.commit()
