"""Write-time data-quality checks: hard bounds and cross-source (ADR-007).

All checks are advisory — they never block a write. These run at write time via
``check_measurement``, wired into both the WritePipeline after-write hook and
webhook/background ingestion. Flag kinds and severity are enum-typed; the
notification channel is the generic ``Notification`` model via ``link``.
"""
from __future__ import annotations

import json
from datetime import tzinfo
from typing import Any

from sqlmodel import col, select

from salus.models.data_quality import DataQualityFlag, DataQualityKind, DataQualitySeverity
from salus.models.measurement import Measurement
from salus.models.metric_definition import MetricDefinition
from salus.models.notification import Notification, NotificationCategory, NotificationSeverity
from salus.models.user import User
from salus.repositories.entity_meta import ENTITY_AFTER_WRITE
from salus.services._helpers import uid
from salus.services.timezone import (
    local_date,
    local_day_range,
    start_of_local_day,
    today_in_tz,
    tz_for,
)

CROSS_SOURCE_DIVERGENCE = 0.25

# Daily aggregate metrics where two sources reporting the same day should agree.
DISCRETE_METRICS: frozenset[str] = frozenset({
    "steps", "sleep", "water", "calories_burned", "active_calories",
    "distance", "elevation_gained", "floors_climbed", "exercise",
})

_TOGGLE_FIELDS: dict[DataQualityKind, str] = {
    DataQualityKind.HARD_BOUND: "dq_notify_hard_bound",
    DataQualityKind.CROSS_SOURCE: "dq_notify_cross_source",
    DataQualityKind.ANOMALY: "dq_notify_anomaly",
}


def _hard_bound_violation(session: Any, measurement: Measurement) -> str | None:
    code = measurement.metric_code
    if not code or measurement.value_numeric is None:
        return None
    definition = session.get(MetricDefinition, code)
    if definition is None:
        return None
    value = measurement.value_numeric
    if definition.min_value is not None and value < definition.min_value:
        return f"{definition.name} value {value} is below plausible minimum {definition.min_value}"
    if definition.max_value is not None and value > definition.max_value:
        return f"{definition.name} value {value} is above plausible maximum {definition.max_value}"
    return None


def _cross_source_violation(session: Any, measurement: Measurement, tz: tzinfo) -> str | None:
    code = measurement.metric_code
    if code not in DISCRETE_METRICS or measurement.value_numeric is None:
        return None
    day = local_date(measurement.start_time, tz)
    start, end = local_day_range(day, tz)
    others = session.exec(
        select(Measurement).where(
            Measurement.user_id == measurement.user_id,
            Measurement.metric_code == code,
            Measurement.source != measurement.source,
            col(Measurement.value_numeric).is_not(None),
            Measurement.start_time >= start,
            Measurement.start_time < end,
            col(Measurement.deleted_at).is_(None),
        )
    ).all()
    for other in others:
        if other.value_numeric and other.value_numeric != 0:
            divergence = abs(measurement.value_numeric - other.value_numeric) / abs(other.value_numeric)
            if divergence > CROSS_SOURCE_DIVERGENCE:
                return (
                    f"{code} differs {divergence:.0%} from source '{other.source}' on {day.isoformat()}"
                )
    return None


def _make_flag(user_id: str, kind: DataQualityKind, measurement: Measurement, message: str) -> DataQualityFlag:
    return DataQualityFlag(
        user_id=user_id,
        kind=kind,
        metric_code=measurement.metric_code,
        measurement_id=measurement.id,
        severity=DataQualitySeverity.WARNING,
        message=message,
        context_json=json.dumps({
            "value": measurement.value_numeric,
            "source": measurement.source,
            "start_time": measurement.start_time.isoformat(),
        }),
    )


def _flag_exists(
    session: Any, user_id: str, measurement_id: str | None, kind: DataQualityKind,
) -> bool:
    if measurement_id is None:
        return False
    return session.exec(
        select(DataQualityFlag).where(
            DataQualityFlag.user_id == user_id,
            DataQualityFlag.measurement_id == measurement_id,
            DataQualityFlag.kind == kind,
        )
    ).first() is not None


def _delete_flags(session: Any, user_id: str, measurement_id: str | None, kinds: set[DataQualityKind]) -> None:
    if measurement_id is None:
        return
    rows = session.exec(
        select(DataQualityFlag).where(
            DataQualityFlag.user_id == user_id,
            DataQualityFlag.measurement_id == measurement_id,
            col(DataQualityFlag.kind).in_(kinds),
        )
    ).all()
    for row in rows:
        session.delete(row)


def _notify_enabled(user: User | None, kind: DataQualityKind) -> bool:
    field = _TOGGLE_FIELDS.get(kind)
    if field is None or user is None:
        return True
    return bool(getattr(user, field, True))


def _metric_link(metric_code: str | None) -> str | None:
    return f"/entries/{metric_code}" if metric_code else None


def _recent_notification_exists(session: Any, user_id: str, link: str | None, tz: tzinfo) -> bool:
    if not link:
        return False
    start = start_of_local_day(today_in_tz(tz), tz)
    return session.exec(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.category == NotificationCategory.DATA_QUALITY,
            col(Notification.link) == link,
            Notification.created_at >= start,
        )
    ).first() is not None


def _notify_data_quality(
    session: Any, user_id: str, kind: DataQualityKind, measurement: Measurement, message: str, tz: tzinfo,
) -> None:
    user = session.get(User, user_id)
    if not _notify_enabled(user, kind):
        return
    if kind != DataQualityKind.ANOMALY and measurement.source == "manual":
        return
    link = _metric_link(measurement.metric_code)
    if _recent_notification_exists(session, user_id, link, tz):
        return
    session.add(Notification(
        user_id=user_id,
        title="Unusual data detected",
        message=message,
        category=NotificationCategory.DATA_QUALITY,
        severity=NotificationSeverity.WARNING,
        link=link,
    ))


def _evaluate_kind(
    session: Any,
    user_id: str,
    instance: Measurement,
    op_type: str,
    kind: DataQualityKind,
    violation: str | None,
    tz: tzinfo,
) -> None:
    """Ensure a flag exists when violated, remove it when resolved on update."""
    if violation:
        if not _flag_exists(session, user_id, instance.id, kind):
            session.add(_make_flag(user_id, kind, instance, violation))
            _notify_data_quality(session, user_id, kind, instance, violation, tz)
    elif op_type == "update":
        _delete_flags(session, user_id, instance.id, {kind})


def check_measurement(
    session: Any, user_id: str, instance: Measurement, op_type: str,
) -> None:
    """Write-time hard-bound + cross-source check (best-effort, non-blocking)."""
    if op_type not in ("create", "update"):
        return
    if instance.metric_code is None or instance.value_numeric is None:
        return

    tz = tz_for(session, user_id)
    _evaluate_kind(
        session, user_id, instance, op_type,
        DataQualityKind.HARD_BOUND, _hard_bound_violation(session, instance), tz,
    )
    _evaluate_kind(
        session, user_id, instance, op_type,
        DataQualityKind.CROSS_SOURCE, _cross_source_violation(session, instance, tz), tz,
    )


def after_measurement_write(
    session: Any, user: User, instance: Measurement, op_type: str,
) -> None:
    check_measurement(session, uid(user), instance, op_type)


def register_write_hooks() -> None:
    ENTITY_AFTER_WRITE["measurement"] = after_measurement_write  # type: ignore[assignment]
