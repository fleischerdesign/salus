"""Data-quality sweep: anomaly detection and cross-source catch-up (ADR-007).

These need a personal baseline or history and run through ``run_checks`` — via the
scheduler and a manual recheck — rather than at write time.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from sqlmodel import col, select

from salus.models.data_quality import DataQualityKind
from salus.models.measurement import Measurement
from salus.services.analytics.stats import zscore_vs_baseline
from salus.services.data_quality.checks import (
    DISCRETE_METRICS,
    _cross_source_violation,
    _flag_exists,
    _make_flag,
    _notify_data_quality,
)
from salus.services.timezone import tz_for

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork

ANOMALY_WINDOW = 14
ANOMALY_Z_THRESHOLD = 3.5
ANOMALY_HISTORY_LIMIT = 90
CROSS_SOURCE_LOOKBACK_DAYS = 7


class DataQualityService:
    def __init__(self, uow: "IUnitOfWork") -> None:
        self.uow = uow

    def run_checks(self, user_id: str) -> dict[str, int]:
        return {
            "anomaly_flags": self._run_anomaly_check(user_id),
            "cross_source_flags": self._run_cross_source_sweep(user_id),
        }

    def _run_anomaly_check(self, user_id: str) -> int:
        session = self.uow.session
        tz = tz_for(session, user_id)
        codes = session.exec(
            select(Measurement.metric_code).where(
                Measurement.user_id == user_id,
                col(Measurement.value_numeric).is_not(None),
                col(Measurement.deleted_at).is_(None),
            ).distinct()
        ).all()

        flagged = 0
        for code in codes:
            if not code:
                continue
            rows = session.exec(
                select(Measurement).where(
                    Measurement.user_id == user_id,
                    Measurement.metric_code == code,
                    col(Measurement.value_numeric).is_not(None),
                    col(Measurement.deleted_at).is_(None),
                ).order_by(col(Measurement.start_time).asc()).limit(ANOMALY_HISTORY_LIMIT)
            ).all()
            if len(rows) < ANOMALY_WINDOW:
                continue

            pairs = [(r, r.value_numeric) for r in rows if r.value_numeric is not None]
            if len(pairs) <= ANOMALY_WINDOW:
                continue
            xs = [value for _, value in pairs]
            zs = zscore_vs_baseline(xs, ANOMALY_WINDOW)
            for (measurement, _), z in zip(pairs, zs):
                if z is None or abs(z) <= ANOMALY_Z_THRESHOLD:
                    continue
                if _flag_exists(session, user_id, measurement.id, DataQualityKind.ANOMALY):
                    continue
                message = f"{code} deviated {abs(z):.1f}σ from your personal baseline"
                session.add(_make_flag(user_id, DataQualityKind.ANOMALY, measurement, message))
                _notify_data_quality(session, user_id, DataQualityKind.ANOMALY, measurement, message, tz)
                flagged += 1
        return flagged

    def _run_cross_source_sweep(self, user_id: str) -> int:
        session = self.uow.session
        tz = tz_for(session, user_id)
        window_start = datetime.now(timezone.utc) - timedelta(days=CROSS_SOURCE_LOOKBACK_DAYS)
        rows = session.exec(
            select(Measurement).where(
                Measurement.user_id == user_id,
                col(Measurement.metric_code).in_(DISCRETE_METRICS),
                col(Measurement.value_numeric).is_not(None),
                Measurement.start_time >= window_start,
                col(Measurement.deleted_at).is_(None),
            )
        ).all()

        flagged = 0
        for measurement in rows:
            cross_source = _cross_source_violation(session, measurement, tz)
            if cross_source and not _flag_exists(session, user_id, measurement.id, DataQualityKind.CROSS_SOURCE):
                session.add(_make_flag(user_id, DataQualityKind.CROSS_SOURCE, measurement, cross_source))
                _notify_data_quality(session, user_id, DataQualityKind.CROSS_SOURCE, measurement, cross_source, tz)
                flagged += 1
        return flagged
