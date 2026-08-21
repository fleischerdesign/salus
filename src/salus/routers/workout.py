from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel

from salus.dependencies import get_current_user, get_workout_service, get_write_pipeline
from salus.exceptions import ApiError, raise_from_command_result
from salus.models.user import User
from salus.schemas.sync import SyncOperation
from salus.schemas.workout import (
    ExerciseResponse,
    ProgramCreate,
    ProgramResponse,
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
    suggested_weight: Optional[float] = None
    is_autoreg_exempt: bool
    reason: str


class ProgramTodayResponse(BaseModel):
    workout_id: Optional[str] = None
    workout_name: Optional[str] = None
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


@router.get("/api/v1/programs", response_model=list[ProgramResponse])
async def list_programs(
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.list_programs(user_id=uid(current_user))


@router.get("/api/v1/programs/{program_id}", response_model=ProgramResponse)
async def get_program(
    program_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_program(user_id=uid(current_user), program_id=program_id)


@router.post(
    "/api/v1/programs",
    response_model=ProgramResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_program(
    data: ProgramCreate,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    service: WorkoutService = Depends(get_workout_service),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="create_program", payload=data.model_dump(mode="json"))]
    )[0]
    raise_from_command_result(result.status, result.message)
    return service.get_program(user_id=uid(current_user), program_id=result.id or "")


@router.delete(
    "/api/v1/programs/{program_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_program(
    program_id: str,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="delete_program", payload={"id": program_id})]
    )[0]
    raise_from_command_result(result.status, result.message)


@router.post("/api/v1/programs/{program_id}/activate", response_model=ProgramResponse)
async def activate_program(
    program_id: str,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    service: WorkoutService = Depends(get_workout_service),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="activate_program", payload={"id": program_id})]
    )[0]
    raise_from_command_result(result.status, result.message)
    return service.get_program(user_id=uid(current_user), program_id=program_id)


@router.post("/api/v1/programs/{program_id}/deactivate", response_model=ProgramResponse)
async def deactivate_program(
    program_id: str,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    service: WorkoutService = Depends(get_workout_service),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="deactivate_program", payload={"id": program_id})]
    )[0]
    raise_from_command_result(result.status, result.message)
    return service.get_program(user_id=uid(current_user), program_id=program_id)


@router.get("/api/v1/programs/{program_id}/today", response_model=ProgramTodayResponse)
async def get_program_today(
    program_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    resolved = service.resolve_today(user_id=uid(current_user), program_id=program_id)
    workout = resolved["workout"]
    return ProgramTodayResponse(
        workout_id=resolved["workout_id"],
        workout_name=workout.name if workout else None,
        reason=resolved["reason"],
    )


@router.get(
    "/api/v1/workouts/{workout_id}/targets",
    response_model=list[WorkoutTargetResponse],
)
async def get_workout_targets(
    workout_id: str,
    date_str: Optional[str] = Query(None),
    progression_scheme: str = Query("autoregulated"),
    current_user: User = Depends(get_current_user),
    service: WorkoutService = Depends(get_workout_service),
):
    return service.get_session_targets(
        user_id=uid(current_user),
        workout_id=workout_id,
        date_str=date_str,
        progression_scheme=progression_scheme,
    )


@router.post("/api/v1/workouts/sessions/start", response_model=WorkoutSessionResponse)
async def start_session(
    workout_id: Optional[str] = Query(None),
    program_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    service: WorkoutService = Depends(get_workout_service),
):
    result = pipeline.process(
        [
            SyncOperation(
                type="command",
                command="start_workout",
                payload={"workout_id": workout_id, "program_id": program_id},
            )
        ]
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
