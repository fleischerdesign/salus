from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from salus.dependencies import get_current_user, get_workout_service, get_write_pipeline
from salus.exceptions import ApiError, raise_from_command_result
from salus.models.user import User
from salus.schemas.sync import SyncOperation
from salus.schemas.workout import (
    ExerciseResponse,
    WorkoutCreate,
    WorkoutResponse,
    WorkoutSetCreate,
    WorkoutSetResponse,
    WorkoutSessionResponse,
)
from salus.services.workout.planner import WorkoutService
from salus.services._helpers import uid
from salus.services.write_pipeline import WritePipeline

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


@router.get("/api/v1/workouts", response_model=list[WorkoutResponse])
async def list_workouts(
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.list_workouts(user_id=uid(current_user))


@router.get(
    "/api/v1/workouts/{workout_id}", response_model=WorkoutResponse
)
async def get_workout(
    workout_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    workout = service.get_workout(user_id=uid(current_user), workout_id=workout_id)
    if not workout:
        raise ApiError(code="not_found", message="Workout not found", status_code=404)
    return workout


@router.post(
    "/api/v1/workouts",
    response_model=WorkoutResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workout(
    data: WorkoutCreate,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    service: WorkoutService = Depends(get_workout_service),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="create_workout", payload=data.model_dump())]
    )[0]
    raise_from_command_result(result.status, result.message)
    return service.get_workout(user_id=uid(current_user), workout_id=result.id or "")


@router.delete(
    "/api/v1/workouts/{workout_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_workout(
    workout_id: str,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="delete_workout", payload={"id": workout_id})]
    )[0]
    raise_from_command_result(result.status, result.message)


@router.get(
    "/api/v1/workouts/{workout_id}/targets",
    response_model=list[WorkoutTargetResponse],
)
async def get_workout_targets(
    workout_id: str,
    date_str: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_session_targets(
        user_id=uid(current_user), workout_id=workout_id, date_str=date_str
    )


@router.post("/api/v1/workouts/sessions/start", response_model=WorkoutSessionResponse)
async def start_session(
    workout_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    service: WorkoutService = Depends(get_workout_service),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="start_workout", payload={"workout_id": workout_id})]
    )[0]
    raise_from_command_result(result.status, result.message)
    session = service.get_active_session(user_id=uid(current_user))
    if not session:
        raise ApiError(code="not_found", message="Workout session not found", status_code=404)
    return session


@router.post("/api/v1/workouts/sessions/complete", response_model=WorkoutSessionResponse)
async def complete_session(
    session_id: str,
    notes: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    service: WorkoutService = Depends(get_workout_service),
):
    result = pipeline.process(
        [
            SyncOperation(
                type="command",
                command="complete_workout",
                payload={"session_id": session_id, "notes": notes},
            )
        ]
    )[0]
    raise_from_command_result(result.status, result.message)
    session = service.get_session(user_id=uid(current_user), session_id=session_id)
    if not session:
        raise ApiError(code="not_found", message="Workout session not found", status_code=404)
    return session


@router.delete("/api/v1/workouts/sessions/log", status_code=status.HTTP_204_NO_CONTENT)
async def delete_logged_set(
    session_id: str,
    exercise_id: str,
    set_number: int,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
):
    result = pipeline.process(
        [
            SyncOperation(
                type="command",
                command="delete_log_set",
                payload={"session_id": session_id, "exercise_id": exercise_id, "set_number": set_number},
            )
        ]
    )[0]
    raise_from_command_result(result.status, result.message)


@router.post("/api/v1/workouts/sessions/log", response_model=WorkoutSetResponse)
async def log_set(
    session_id: str,
    entry: WorkoutSetCreate,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    service: WorkoutService = Depends(get_workout_service),
):
    result = pipeline.process(
        [
            SyncOperation(
                type="command",
                command="log_set",
                payload={"session_id": session_id, **entry.model_dump()},
            )
        ]
    )[0]
    raise_from_command_result(result.status, result.message)
    record = result.record or {}
    exercise = service.get_exercise(user_id=uid(current_user), exercise_id=record.get("exercise_id") or "")
    return WorkoutSetResponse(
        id=record.get("id", ""),
        session_id=record.get("session_id", ""),
        exercise_id=record.get("exercise_id", ""),
        set_number=record.get("set_number", 0),
        weight=record.get("weight", 0.0),
        reps=record.get("reps", 0),
        rpe=record.get("rpe"),
        exercise=ExerciseResponse.model_validate(exercise) if exercise else None,  # pyright: ignore[reportArgumentType]
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
