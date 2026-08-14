from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from salus.models.fasting import FastingSession
from salus.models.measurement import Measurement
from salus.services._helpers import uid
from salus.services.command_registry import CommandResult, register
from salus.services.serialization import serialize_record

if TYPE_CHECKING:
    from salus.models.user import User
    from salus.repositories.unit_of_work import IUnitOfWork

FASTING_SOURCE = "fasting"
FASTING_METRIC_CODE = "fasting_hours"

_SESSION_FIELDS = (
    "id", "user_id", "started_at", "ended_at", "target_hours", "fasting_type",
    "water_only", "notes", "mood_during", "difficulty", "created_at",
    "updated_at", "deleted_at",
)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def _now_utc() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _session_measurement(session: FastingSession, hours: float) -> Measurement:
    return Measurement(
        user_id=session.user_id,
        metric_code=FASTING_METRIC_CODE,
        source_data_type=FASTING_SOURCE,
        source=FASTING_SOURCE,
        value_numeric=round(hours, 2),
        start_time=session.started_at,
        end_time=session.ended_at,
        external_id=session.id,
    )


def _delete_measurement(uow: IUnitOfWork, session_id: str) -> None:
    existing = uow.measurements.find_by_external_id(session_id, FASTING_SOURCE)
    if existing:
        uow.measurements.delete(existing)


@register("start_fasting_session")
class StartFastingSessionHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        user_id = uid(user)

        active = uow.fasting_sessions.find_active_by_user(user_id)
        if active:
            return CommandResult(
                status="created",
                id=active.id,
                record=serialize_record(active, list(_SESSION_FIELDS)),
            )

        now = _now_utc()
        started_at = _parse_datetime(payload.get("started_at")) or now
        session = FastingSession(
            id=payload.get("id"),
            user_id=user_id,
            started_at=started_at,
            target_hours=float(payload.get("target_hours", 16.0)),
            fasting_type=payload.get("fasting_type", "intermittent"),
            water_only=bool(payload.get("water_only", True)),
            notes=payload.get("notes"),
            created_at=now,
            updated_at=now,
        )
        uow.fasting_sessions.add(session)
        uow.commit()
        uow.session.refresh(session)
        return CommandResult(
            status="created",
            id=session.id,
            record=serialize_record(session, list(_SESSION_FIELDS)),
        )


@register("end_fasting_session")
class EndFastingSessionHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        user_id = uid(user)
        session_id = payload.get("session_id")
        if not session_id:
            return CommandResult(status="error", message="session_id is required")

        session = uow.fasting_sessions.get_by_id(session_id)
        if not session or session.user_id != user_id:
            return CommandResult(status="not_found", message="Fasting session not found")
        if session.ended_at is not None:
            return CommandResult(
                status="updated",
                id=session.id,
                record=serialize_record(session, list(_SESSION_FIELDS)),
            )

        session.ended_at = _parse_datetime(payload.get("ended_at")) or _now_utc()
        session.updated_at = _now_utc()
        uow.fasting_sessions.add(session)

        hours = (session.ended_at - session.started_at).total_seconds() / 3600.0
        uow.measurements.add(_session_measurement(session, hours))

        uow.commit()
        uow.session.refresh(session)
        return CommandResult(
            status="updated",
            id=session.id,
            record=serialize_record(session, list(_SESSION_FIELDS)),
        )


@register("cancel_fasting_session")
class CancelFastingSessionHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        user_id = uid(user)
        session_id = payload.get("session_id")
        if not session_id:
            return CommandResult(status="error", message="session_id is required")

        session = uow.fasting_sessions.get_by_id(session_id)
        if not session or session.user_id != user_id:
            return CommandResult(status="deleted", id=session_id)
        if session.ended_at is not None:
            return CommandResult(status="error", message="Cannot cancel a completed fasting session")

        uow.fasting_sessions.delete(session)
        uow.commit()
        return CommandResult(status="deleted", id=session_id)


@register("delete_fasting_session")
class DeleteFastingSessionHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        user_id = uid(user)
        session_id = payload.get("session_id")
        if not session_id:
            return CommandResult(status="error", message="session_id is required")

        session = uow.fasting_sessions.get_by_id(session_id)
        if not session or session.user_id != user_id:
            return CommandResult(status="deleted", id=session_id)

        _delete_measurement(uow, session_id)
        uow.fasting_sessions.delete(session)
        uow.commit()
        return CommandResult(status="deleted", id=session_id)
