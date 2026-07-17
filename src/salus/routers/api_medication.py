from fastapi import APIRouter, Depends, Response

from salus.dependencies import get_current_user, get_medication_service
from salus.models.user import User
from salus.schemas.medication import (
    MedicationCreate,
    MedicationInventoryResponse,
    MedicationInventoryUpdate,
    MedicationLogCreate,
    MedicationLogResponse,
    MedicationResponse,
    MedicationScheduleCreate,
    MedicationScheduleResponse,
    MedicationTodayResponse,
    MedicationUpdate,
)
from salus.services._helpers import uid
from salus.services.medication import MedicationService

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


# ── Medication CRUD ──


@router.get("", response_model=list[MedicationResponse])
async def list_medications(
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    medications = medication_svc.find_all(uid(current_user))
    return [_medication_to_response(m) for m in medications]


@router.post("", response_model=MedicationResponse, status_code=201)
async def create_medication(
    data: MedicationCreate,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    m = medication_svc.create(data, uid(current_user))
    return _medication_to_response(m)


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


@router.get("/{medication_id}", response_model=MedicationResponse)
async def get_medication(
    medication_id: str,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    m = medication_svc.get(medication_id, uid(current_user))
    return _medication_to_response(m)


@router.put("/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: str,
    data: MedicationUpdate,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    m = medication_svc.update(medication_id, uid(current_user), data)
    return _medication_to_response(m)


@router.delete("/{medication_id}", status_code=204)
async def delete_medication(
    medication_id: str,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    medication_svc.delete(medication_id, uid(current_user))
    return Response(status_code=204)


# ── Schedule ──


@router.get("/{medication_id}/schedule", response_model=list[MedicationScheduleResponse])
async def get_schedules(
    medication_id: str,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    schedules = medication_svc.get_schedules(medication_id, uid(current_user))
    return [_schedule_to_response(s) for s in schedules]


@router.post(
    "/{medication_id}/schedule",
    response_model=MedicationScheduleResponse,
    status_code=201,
)
async def create_schedule(
    medication_id: str,
    data: MedicationScheduleCreate,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    s = medication_svc.add_schedule(medication_id, uid(current_user), data)
    return _schedule_to_response(s)


@router.delete("/schedule/{schedule_id}", status_code=204)
async def delete_schedule(
    schedule_id: str,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    medication_svc.delete_schedule(schedule_id, uid(current_user))
    return Response(status_code=204)


# ── Log ──


@router.post("/{medication_id}/log", response_model=MedicationLogResponse, status_code=201)
async def log_intake(
    medication_id: str,
    data: MedicationLogCreate,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    log = medication_svc.log_intake(medication_id, uid(current_user), data)
    return _log_to_response(log)


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


@router.put(
    "/{medication_id}/inventory",
    response_model=MedicationInventoryResponse,
)
async def update_inventory(
    medication_id: str,
    data: MedicationInventoryUpdate,
    current_user: User = Depends(get_current_user),
    medication_svc: MedicationService = Depends(get_medication_service),
):
    inv = medication_svc.update_inventory(medication_id, uid(current_user), data)
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
