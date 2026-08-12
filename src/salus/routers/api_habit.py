from fastapi import APIRouter, Depends

from salus.dependencies import get_current_user, get_event_bus, get_habit_service
from salus.models.user import User
from salus.schemas.habit import HabitCheckResponse, HabitStatsResponse
from salus.services._helpers import uid
from salus.services.event_bus import EventBus, schedule_publish
from salus.services.habit import HabitService

router = APIRouter(prefix="/api/v1/habits")


@router.post("/{habit_id}/check", response_model=HabitCheckResponse)
async def toggle_check(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    habit_svc: HabitService = Depends(get_habit_service),
    event_bus: EventBus = Depends(get_event_bus),
):
    result = habit_svc.toggle_check(habit_id, uid(current_user))
    schedule_publish(event_bus, uid(current_user))
    return HabitCheckResponse(**result)


@router.get("/{habit_id}/stats", response_model=HabitStatsResponse)
async def get_stats(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    habit_svc: HabitService = Depends(get_habit_service),
):
    stats = habit_svc.get_stats(habit_id, uid(current_user))
    return HabitStatsResponse(**stats)
