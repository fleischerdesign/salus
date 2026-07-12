from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

from salus.dependencies import get_current_user, get_workout_service
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
        return JSONResponse(status_code=400, content={"detail": str(e)})


@router.delete(
    "/api/v1/workouts/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    service.delete_exercise(user_id=uid(current_user), exercise_id=exercise_id)


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
    plan_id: int,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    service.delete_plan(user_id=uid(current_user), plan_id=plan_id)


@router.post("/api/v1/workouts/sessions/start", response_model=WorkoutSessionResponse)
async def start_session(
    plan_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.start_session(user_id=uid(current_user), plan_id=plan_id)


@router.post("/api/v1/workouts/sessions/log", response_model=WorkoutLogEntryResponse)
async def log_set(
    session_id: int,
    entry: WorkoutLogEntryCreate,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.log_set(
        user_id=uid(current_user), session_id=session_id, entry=entry
    )


@router.delete("/api/v1/workouts/sessions/log", status_code=status.HTTP_204_NO_CONTENT)
async def delete_logged_set(
    session_id: int,
    exercise_id: int,
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


@router.post(
    "/api/v1/workouts/sessions/complete", response_model=WorkoutSessionResponse
)
async def complete_session(
    session_id: int,
    notes: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.complete_session(
        user_id=uid(current_user), session_id=session_id, notes=notes
    )
