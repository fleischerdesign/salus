from fastapi import APIRouter, Depends, Response

from salus.dependencies import get_current_user, get_habit_service
from salus.models.user import User
from salus.schemas.habit import (
    HabitCheckResponse,
    HabitCreate,
    HabitResponse,
    HabitStatsResponse,
    HabitUpdate,
)
from salus.services._helpers import uid
from salus.services.habit import HabitService

router = APIRouter(prefix="/api/v1/habits")


def _habit_to_response(h, stats: dict | None = None) -> dict:
    s = stats or {}
    return {
        "id": h.id,
        "name": h.name,
        "description": h.description,
        "color": h.color,
        "icon": h.icon,
        "frequency": h.frequency.value if hasattr(h.frequency, "value") else str(h.frequency),
        "target_count": h.target_count,
        "days_bitmask": h.days_bitmask,
        "stack_hint": h.stack_hint,
        "is_archived": h.is_archived,
        "created_at": h.created_at.isoformat() if h.created_at else "",
        "current_streak": s.get("current_streak", 0),
        "longest_streak": s.get("longest_streak", 0),
        "completion_rate": s.get("completion_rate", 0.0),
        "today_completed": s.get("today_completed", False),
    }


@router.get("", response_model=list[HabitResponse])
async def list_habits(
    current_user: User = Depends(get_current_user),
    habit_svc: HabitService = Depends(get_habit_service),
):
    habits = habit_svc.find_all(uid(current_user))
    stats = habit_svc.get_all_habits_stats(uid(current_user))
    return [_habit_to_response(h, stats.get(h.id or "")) for h in habits]


@router.post("", response_model=HabitResponse, status_code=201)
async def create_habit(
    data: HabitCreate,
    current_user: User = Depends(get_current_user),
    habit_svc: HabitService = Depends(get_habit_service),
):
    h = habit_svc.create(data, uid(current_user))
    return _habit_to_response(h)


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    habit_svc: HabitService = Depends(get_habit_service),
):
    h = habit_svc.get(habit_id, uid(current_user))
    s = habit_svc.get_stats(habit_id, uid(current_user))
    return _habit_to_response(h, s)


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: str,
    data: HabitUpdate,
    current_user: User = Depends(get_current_user),
    habit_svc: HabitService = Depends(get_habit_service),
):
    h = habit_svc.update(habit_id, uid(current_user), data)
    return _habit_to_response(h)


@router.delete("/{habit_id}", status_code=204)
async def delete_habit(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    habit_svc: HabitService = Depends(get_habit_service),
):
    habit_svc.delete(habit_id, uid(current_user))
    return Response(status_code=204)


@router.post("/{habit_id}/check", response_model=HabitCheckResponse)
async def toggle_check(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    habit_svc: HabitService = Depends(get_habit_service),
):
    result = habit_svc.toggle_check(habit_id, uid(current_user))
    return HabitCheckResponse(**result)


@router.get("/{habit_id}/stats", response_model=HabitStatsResponse)
async def get_stats(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    habit_svc: HabitService = Depends(get_habit_service),
):
    stats = habit_svc.get_stats(habit_id, uid(current_user))
    return HabitStatsResponse(**stats)
