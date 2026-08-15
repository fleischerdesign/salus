from fastapi import APIRouter, Depends, Response

from salus.dependencies import (
    get_current_user,
    get_medication_service,
    get_write_pipeline,
)
from salus.exceptions import raise_from_command_result
from salus.models.user import User
from salus.schemas.medication import (
    MedicationInventoryResponse,
    MedicationLogCreate,
    MedicationLogResponse,
    MedicationScheduleResponse,
    MedicationTodayResponse,
)
from salus.schemas.sync import SyncOperation
from salus.services._helpers import uid
from salus.services.medication import MedicationService
from salus.services.write_pipeline import WritePipeline

router = APIRouter(prefix="/api/v1/medications")


def _medication_to_response(m) -> dict:
    return {
        "id": m.id,
        "name": m.name,
        "active_ingredient": m.active_ingredient,
        "strength": m.strength,
        "form": m.form,
        "instructions": m.instructions,
        "color_hex": m.color_hex,
        "icon": m.icon,
        "is_active": m.is_active,
        "created_at": m.created_at.isoformat() if m.created_at else "",
    }


def _schedule_to_response(s) -> dict:
    return {
        "id": s.id,
        "medication_id": s.medication_id,
        "dosage": s.dosage,
        "times": s.times,
        "days_of_week": s.days_of_week,
        "start_date": s.start_date.isoformat() if s.start_date else None,
        "end_date": s.end_date.isoformat() if s.end_date else None,
    }


def _log_to_response(log) -> dict:
    return {
        "id": log.id,
        "medication_id": log.medication_id,
        "schedule_id": log.schedule_id,
        "taken_at": log.taken_at.isoformat() if log.taken_at else None,
        "dosage_taken": log.dosage_taken,
        "skipped": log.skipped,
        "notes": log.notes,
        "created_at": log.created_at.isoformat() if log.created_at else "",
    }


# ── Today view ──


@router.get("/today", response_model=MedicationTodayResponse)
async def get_today(
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    result = medication_svc.get_today(uid(current_user))
    return {
        "items": result["items"],
        "as_needed": [_medication_to_response(m) for m in result["as_needed"]],
    }


# ── Schedule ──


@router.get("/{medication_id}/schedule", response_model=list[MedicationScheduleResponse])
async def get_schedules(
    medication_id: str,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    schedules = medication_svc.get_schedules(medication_id, uid(current_user))
    return [_schedule_to_response(s) for s in schedules]


# ── Log ──


@router.post("/{medication_id}/log", response_model=MedicationLogResponse, status_code=201)
async def log_intake(
    medication_id: str,
    data: MedicationLogCreate,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
):
    result = pipeline.process(
        [
            SyncOperation(
                type="command",
                command="log_medication",
                payload={"medication_id": medication_id, **data.model_dump()},
            )
        ]
    )[0]
    raise_from_command_result(result.status, result.message)
    return result.record or {}


@router.get("/{medication_id}/log", response_model=list[MedicationLogResponse])
async def get_logs(
    medication_id: str,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    logs = medication_svc.get_logs(medication_id, uid(current_user))
    return [_log_to_response(log) for log in logs]


# ── Inventory ──


@router.get(
    "/{medication_id}/inventory",
    response_model=MedicationInventoryResponse | dict,
)
async def get_inventory(
    medication_id: str,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    inv = medication_svc.get_inventory(medication_id, uid(current_user))
    if inv is None:
        return Response(status_code=204)
    return {
        "id": inv.id,
        "medication_id": inv.medication_id,
        "initial_count": inv.initial_count,
        "remaining_count": inv.remaining_count,
        "refill_at_count": inv.refill_at_count,
        "prescription_refills": inv.prescription_refills,
        "next_refill_date": inv.next_refill_date.isoformat() if inv.next_refill_date else None,
        "needs_refill": inv.remaining_count <= inv.refill_at_count,
    }
