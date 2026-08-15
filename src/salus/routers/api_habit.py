from fastapi import APIRouter, Depends

from salus.dependencies import get_current_user, get_habit_service, get_write_pipeline
from salus.exceptions import raise_from_command_result
from salus.models.user import User
from salus.schemas.habit import HabitCheckResponse, HabitStatsResponse
from salus.schemas.sync import SyncOperation
from salus.services._helpers import uid
from salus.services.habit import HabitService
from salus.services.write_pipeline import WritePipeline

router = APIRouter(prefix="/api/v1/habits")


@router.post("/{habit_id}/check", response_model=HabitCheckResponse)
async def toggle_check(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="toggle_habit_check", payload={"habit_id": habit_id})]
    )[0]
    raise_from_command_result(result.status, result.message)
    extra = result.extra or {}
    return HabitCheckResponse(
        completed=extra["completed"],
        current_streak=extra["current_streak"],
        longest_streak=extra["longest_streak"],
        completion_rate=extra["completion_rate"],
    )


@router.get("/{habit_id}/stats", response_model=HabitStatsResponse)
async def get_stats(
    habit_id: str,
    current_user: User = Depends(get_current_user),
    habit_svc: HabitService = Depends(get_habit_service),
):
    stats = habit_svc.get_stats(habit_id, uid(current_user))
    return HabitStatsResponse(**stats)
