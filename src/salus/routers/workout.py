from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from salus.dependencies import get_current_user, get_workout_service
from salus.exceptions import ApiError
from salus.models.user import User
from salus.schemas.workout import (
    ExerciseCreate,
    ExerciseResponse,
    WorkoutPlanCreate,
    WorkoutPlanResponse,
    WorkoutLogEntryCreate,
    WorkoutLogEntryResponse,
    WorkoutSessionResponse,
)
from salus.services.workout.planner import WorkoutService
from salus.services._helpers import uid

router = APIRouter(tags=["Workouts"])


class WorkoutTargetResponse(BaseModel):
    exercise_id: str
    name: str
    suggested_sets: int
    suggested_reps: int
    suggested_rpe: float
    weight_multiplier: float
    is_autoreg_exempt: bool
    reason: str


@router.post(
    "/api/v1/workouts/exercises",
    response_model=ExerciseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_exercise(
    data: ExerciseCreate,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    try:
        return service.create_exercise(user_id=uid(current_user), data=data)
    except ValueError as e:
        raise ApiError(code="validation_error", message=str(e), status_code=400)


@router.get(
    "/api/v1/workouts/exercises", response_model=list[ExerciseResponse]
)
async def list_exercises(
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_exercise_catalog(user_id=uid(current_user))


@router.get(
    "/api/v1/workouts/exercises/{exercise_id}", response_model=ExerciseResponse
)
async def get_exercise(
    exercise_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    ex = service.get_exercise(user_id=uid(current_user), exercise_id=exercise_id)
    if not ex:
        raise ApiError(code="not_found", message="Exercise not found", status_code=404)
    return ex


@router.delete(
    "/api/v1/workouts/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_exercise(
    exercise_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    service.delete_exercise(user_id=uid(current_user), exercise_id=exercise_id)


@router.get("/api/v1/workouts/plans", response_model=list[WorkoutPlanResponse])
async def list_plans(
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.list_plans(user_id=uid(current_user))


@router.get(
    "/api/v1/workouts/plans/{plan_id}", response_model=WorkoutPlanResponse
)
async def get_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    plan = service.get_plan(user_id=uid(current_user), plan_id=plan_id)
    if not plan:
        raise ApiError(code="not_found", message="Plan not found", status_code=404)
    return plan


@router.post(
    "/api/v1/workouts/plans",
    response_model=WorkoutPlanResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_plan(
    data: WorkoutPlanCreate,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.create_plan(user_id=uid(current_user), data=data)


@router.delete(
    "/api/v1/workouts/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    service.delete_plan(user_id=uid(current_user), plan_id=plan_id)


@router.get(
    "/api/v1/workouts/plans/{plan_id}/targets",
    response_model=list[WorkoutTargetResponse],
)
async def get_plan_targets(
    plan_id: str,
    date_str: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_session_targets(
        user_id=uid(current_user), plan_id=plan_id, date_str=date_str
    )


@router.post("/api/v1/workouts/sessions/start", response_model=WorkoutSessionResponse)
async def start_session(
    plan_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.start_session(user_id=uid(current_user), plan_id=plan_id)


@router.post("/api/v1/workouts/sessions/complete", response_model=WorkoutSessionResponse)
async def complete_session(
    session_id: str,
    notes: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.complete_session(
        user_id=uid(current_user), session_id=session_id, notes=notes
    )


@router.delete("/api/v1/workouts/sessions/log", status_code=status.HTTP_204_NO_CONTENT)
async def delete_logged_set(
    session_id: str,
    exercise_id: str,
    set_number: int,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    service.delete_logged_set(
        user_id=uid(current_user),
        session_id=session_id,
        exercise_id=exercise_id,
        set_number=set_number,
    )


@router.post("/api/v1/workouts/sessions/log", response_model=WorkoutLogEntryResponse)
async def log_set(
    session_id: str,
    entry: WorkoutLogEntryCreate,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.log_set(
        user_id=uid(current_user), session_id=session_id, entry=entry
    )


@router.get(
    "/api/v1/workouts/sessions/active", response_model=WorkoutSessionResponse | None
)
async def get_active_session(
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_active_session(user_id=uid(current_user))


@router.get(
    "/api/v1/workouts/sessions/recent", response_model=list[WorkoutSessionResponse]
)
async def get_recent_sessions(
    limit: int = Query(10),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_recent_sessions(user_id=uid(current_user), limit=limit)
