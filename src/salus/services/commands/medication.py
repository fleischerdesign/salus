from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from salus.models.medication import MedicationLog
from salus.schemas.commands import (
    DeleteMedicationLogPayload,
    LogMedicationPayload,
    SkipMedicationDosePayload,
)
from salus.services._helpers import uid
from salus.services.command_registry import CommandResult, register
from salus.services.medication import _make_dt
from salus.services.serialization import serialize_record
from salus.services.timezone import today_in_tz, tz_for

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User

_LOG_FIELDS = (
    "id", "medication_id", "user_id", "schedule_id", "taken_at",
    "dosage_taken", "skipped", "notes", "created_at", "deleted_at",
)


def _resolve_medication(
    uow: IUnitOfWork, user_id: str, medication_id: str
) -> CommandResult | None:
    med = uow.medications.get_by_id(medication_id)
    if not med or med.user_id != user_id:
        return CommandResult(status="not_found", message="Medication not found")
    return None


@register("log_medication")
class LogMedicationHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = LogMedicationPayload.model_validate(payload)
        user_id = uid(user)
        error = _resolve_medication(uow, user_id, data.medication_id)
        if error:
            return error

        log = MedicationLog(
            id=data.id,
            medication_id=data.medication_id,
            user_id=user_id,
            schedule_id=data.schedule_id,
            taken_at=datetime.fromisoformat(data.taken_at) if data.taken_at else datetime.now(timezone.utc),
            dosage_taken=data.dosage_taken,
            skipped=data.skipped,
            notes=data.notes,
        )
        uow.medication_logs.add(log)
        uow.commit()
        uow.session.refresh(log)
        return CommandResult(
            status="created",
            id=log.id,
            record=serialize_record(log, list(_LOG_FIELDS)),
        )


@register("skip_medication_dose")
class SkipMedicationDoseHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = SkipMedicationDosePayload.model_validate(payload)
        user_id = uid(user)
        error = _resolve_medication(uow, user_id, data.medication_id)
        if error:
            return error

        tz = tz_for(uow.session, user_id)
        hour, minute = map(int, data.scheduled_time.split(":"))
        taken_at = _make_dt(today_in_tz(tz), hour, minute, tz)

        log = MedicationLog(
            id=data.id,
            medication_id=data.medication_id,
            user_id=user_id,
            schedule_id=data.schedule_id,
            taken_at=taken_at,
            skipped=True,
        )
        uow.medication_logs.add(log)
        uow.commit()
        uow.session.refresh(log)
        return CommandResult(
            status="created",
            id=log.id,
            record=serialize_record(log, list(_LOG_FIELDS)),
        )


@register("delete_medication_log")
class DeleteMedicationLogHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = DeleteMedicationLogPayload.model_validate(payload)
        log = uow.medication_logs.get_by_id(data.id)
        if not log:
            return CommandResult(status="deleted", id=data.id)
        if log.user_id != uid(user):
            return CommandResult(status="forbidden", message="Not your medication log")

        log.deleted_at = datetime.now(timezone.utc)
        uow.medication_logs.add(log)
        uow.commit()
        return CommandResult(status="deleted", id=data.id)
