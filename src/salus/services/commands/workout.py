from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, TYPE_CHECKING

from salus.models.workout import Program, ProgramWorkout, WorkoutSet, Workout, WorkoutExercise, WorkoutSession
from salus.utils import uuid7_str
from salus.services._helpers import uid
from salus.services.command_registry import CommandResult, register
from salus.services.constants import DEFAULT_TARGET_REPS, DEFAULT_TARGET_RPE, DEFAULT_TARGET_SETS
from salus.services.serialization import serialize_record

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User


def _new_uuid() -> str:
    return uuid7_str()


_SESSION_FIELDS = (
    "id", "user_id", "workout_id", "program_id", "started_at", "completed_at",
    "progression_scheme", "recovery_score", "notes", "created_at", "updated_at", "deleted_at",
)

_SET_FIELDS = (
    "id", "session_id", "exercise_id", "set_number", "weight", "reps",
    "rpe", "created_at", "updated_at", "deleted_at",
)


def _serialize_session(session: WorkoutSession) -> dict[str, Any]:
    return serialize_record(session, list(_SESSION_FIELDS))


def _serialize_set(entry: WorkoutSet) -> dict[str, Any]:
    return serialize_record(entry, list(_SET_FIELDS))


@register("start_workout")
class StartWorkoutHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        workout_id = payload.get("workout_id")
        program_id = payload.get("program_id")
        session_id = payload.get("id")

        active = uow.workout_sessions.find_active_by_user(user.id)  # pyright: ignore[reportArgumentType]
        if active:
            return CommandResult(status="created", record=_serialize_session(active), id=active.id)

        progression_scheme = "autoregulated"
        recovery_score = None
        if program_id:
            program = uow.programs.get_by_id(program_id)
            if program and program.user_id == user.id:  # pyright: ignore[reportAttributeAccessIssue]
                progression_scheme = program.progression_scheme
                if progression_scheme != "none":
                    recovery_score = self._calculate_recovery(uow, user)

        now = datetime.now(timezone.utc)
        session = WorkoutSession(
            id=session_id,
            user_id=user.id,  # pyright: ignore[reportArgumentType]
            workout_id=workout_id,
            program_id=program_id,
            started_at=now,
            progression_scheme=progression_scheme,
            recovery_score=recovery_score,
            created_at=now,
            updated_at=now,
        )
        uow.workout_sessions.add(session)
        uow.commit()
        uow.session.refresh(session)
        return CommandResult(status="created", record=_serialize_session(session), id=session.id)

    @staticmethod
    def _calculate_recovery(uow: IUnitOfWork, user: User) -> float:
        from salus.services.workout.autoregulation import build_autoregulation_service

        user_id = uid(user)
        autoreg_svc = build_autoregulation_service(uow)
        overall, _, _, _ = autoreg_svc.calculate_recovery_score(user_id)
        return overall


@register("complete_workout")
class CompleteWorkoutHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        session_id = payload.get("session_id")
        notes = payload.get("notes")

        if not session_id:
            return CommandResult(status="error", message="session_id is required")

        session = self._resolve_session(uow, user, session_id)
        if not session:
            return CommandResult(status="not_found", message="Workout session not found")
        if session.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", message="Not your workout session")

        session.completed_at = datetime.now(timezone.utc)
        if notes is not None:
            session.notes = notes
        uow.workout_sessions.update(session)
        uow.commit()
        uow.session.refresh(session)
        return CommandResult(status="updated", record=_serialize_session(session), id=session_id)

    @staticmethod
    def _resolve_session(uow: IUnitOfWork, user: User, session_id: str) -> Any:
        if session_id in ("0", "active"):
            return uow.workout_sessions.find_active_by_user(user.id)  # pyright: ignore[reportArgumentType]
        return uow.workout_sessions.get_by_id(session_id)  # pyright: ignore[reportArgumentType]


@register("cancel_workout")
class CancelWorkoutHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        session_id = payload.get("session_id")
        if not session_id:
            return CommandResult(status="error", message="session_id is required")

        session = uow.workout_sessions.get_by_id(session_id)  # pyright: ignore[reportArgumentType]
        if not session:
            return CommandResult(status="deleted", id=session_id)
        if session.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", message="Not your workout session")

        session.deleted_at = datetime.now(timezone.utc)
        uow.workout_sessions.add(session)
        uow.commit()
        return CommandResult(status="deleted", id=session_id)


@register("log_set")
class LogSetHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        session_id = payload.get("session_id") or ""
        exercise_id = payload.get("exercise_id") or ""
        set_number = payload.get("set_number") or 0
        weight = payload.get("weight") or 0.0
        reps = payload.get("reps") or 0
        rpe = payload.get("rpe")
        entry_id = payload.get("id")

        if not session_id:
            return CommandResult(status="error", message="session_id is required")

        session = self._resolve_session(uow, user, session_id)
        if not session:
            return CommandResult(status="not_found", message="Workout session not found")
        if session.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", message="Not your workout session")

        now = datetime.now(timezone.utc)
        entry = WorkoutSet(
            id=entry_id,
            session_id=session.id,
            exercise_id=exercise_id,
            set_number=set_number,
            weight=weight,
            reps=reps,
            rpe=rpe,
            created_at=now,
            updated_at=now,
        )
        uow.workout_sets.add(entry)
        uow.commit()
        uow.session.refresh(entry)
        return CommandResult(status="created", record=_serialize_set(entry), id=entry.id)

    @staticmethod
    def _resolve_session(uow: IUnitOfWork, user: User, session_id: str) -> Any:
        if session_id in ("0", "active"):
            return uow.workout_sessions.find_active_by_user(user.id)  # pyright: ignore[reportArgumentType]
        return uow.workout_sessions.get_by_id(session_id)  # pyright: ignore[reportArgumentType]


@register("delete_log_set")
class DeleteLogSetHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        entry_id = payload.get("id")
        if not entry_id:
            session_id = payload.get("session_id")
            exercise_id = payload.get("exercise_id")
            set_number = payload.get("set_number")
            if not (session_id and exercise_id and set_number is not None):
                return CommandResult(status="error", message="id or (session_id, exercise_id, set_number) is required")
            entry = uow.workout_sets.find_by_session_exercise_set(
                session_id, exercise_id, set_number
            )
            if entry is None:
                return CommandResult(status="deleted", id=None)
            entry_id = entry.id or ""

        from sqlmodel import select

        stmt = select(WorkoutSet).where(WorkoutSet.id == entry_id)
        entry = uow.session.exec(stmt).first()
        if not entry:
            return CommandResult(status="deleted", id=entry_id)

        session = uow.workout_sessions.get_by_id(entry.session_id)  # pyright: ignore[reportArgumentType]
        if not session or session.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", message="Not your workout session")

        entry.deleted_at = datetime.now(timezone.utc)
        uow.session.add(entry)
        uow.commit()
        return CommandResult(status="deleted", id=entry_id)


@register("create_workout")
class CreateWorkoutHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        name = payload.get("name", "").strip()
        if not name:
            return CommandResult(status="error", message="name is required")

        now = datetime.now(timezone.utc)
        workout_id = payload.get("id") or _new_uuid()
        workout = Workout(
            id=workout_id,
            name=name,
            description=payload.get("description"),
            user_id=user.id,  # pyright: ignore[reportArgumentType]
            position=payload.get("position", 0),
            created_at=now,
            updated_at=now,
        )

        exercises = payload.get("exercises", [])
        for item in exercises:
            exercise_id = item.get("exercise_id")
            ex = uow.exercises.get_by_id(exercise_id)  # pyright: ignore[reportArgumentType]
            if not ex:
                return CommandResult(status="error", message=f"Exercise {exercise_id} not found")
            workout_ex = WorkoutExercise(
                id=item.get("id"),
                workout_id=workout_id,
                exercise_id=exercise_id,
                sequence=item.get("sequence", 0),
                target_sets=item.get("target_sets", DEFAULT_TARGET_SETS),
                target_reps=item.get("target_reps", DEFAULT_TARGET_REPS),
                target_rpe=item.get("target_rpe", DEFAULT_TARGET_RPE),
                is_autoreg_exempt=item.get("is_autoreg_exempt", False),
                rest_seconds=item.get("rest_seconds"),
                created_at=now,
                updated_at=now,
            )
            uow.workout_exercises.add(workout_ex)
        uow.workouts.add(workout)
        uow.commit()

        record: dict[str, Any] = {"id": workout_id, "name": workout.name,
            "description": workout.description}
        return CommandResult(status="created", record=record, id=workout_id)


@register("delete_workout")
class DeleteWorkoutHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        workout_id = payload.get("id")
        if not workout_id:
            return CommandResult(status="error", message="id is required")
        workout = uow.workouts.get_by_id(workout_id)  # pyright: ignore[reportArgumentType]
        if not workout:
            return CommandResult(status="deleted", id=workout_id)
        if workout.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", id=workout_id)
        for workout_ex in uow.workout_exercises.find_by_workout(workout_id):
            uow.workout_exercises.delete(workout_ex)
        uow.workouts.delete(workout)
        uow.commit()
        return CommandResult(status="deleted", id=workout_id)


@register("create_program")
class CreateProgramHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        name = payload.get("name", "").strip()
        if not name:
            return CommandResult(status="error", message="name is required")

        now = datetime.now(timezone.utc)
        program_id = payload.get("id") or _new_uuid()
        program = Program(
            id=program_id,
            name=name,
            description=payload.get("description"),
            user_id=user.id,  # pyright: ignore[reportArgumentType]
            progression_scheme=payload.get("progression_scheme", "autoregulated"),
            position=payload.get("position", 0),
            created_at=now,
            updated_at=now,
        )

        for item in payload.get("slots", []):
            slot_workout_id = item.get("workout_id")
            if not uow.workouts.get_by_id(slot_workout_id):  # pyright: ignore[reportArgumentType]
                return CommandResult(status="error", message=f"Workout {slot_workout_id} not found")
            scheduled_date_raw = item.get("scheduled_date")
            slot = ProgramWorkout(
                id=item.get("id"),
                program_id=program_id,
                workout_id=slot_workout_id,
                sequence=item.get("sequence", 0),
                day_of_week=item.get("day_of_week"),
                scheduled_date=date.fromisoformat(scheduled_date_raw) if scheduled_date_raw else None,
                created_at=now,
                updated_at=now,
            )
            uow.program_workouts.add(slot)
        uow.programs.add(program)
        uow.commit()

        record: dict[str, Any] = {"id": program_id, "name": program.name,
            "description": program.description, "progression_scheme": program.progression_scheme}
        return CommandResult(status="created", record=record, id=program_id)


@register("delete_program")
class DeleteProgramHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        program_id = payload.get("id")
        if not program_id:
            return CommandResult(status="error", message="id is required")
        program = uow.programs.get_by_id(program_id)  # pyright: ignore[reportArgumentType]
        if not program:
            return CommandResult(status="deleted", id=program_id)
        if program.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", id=program_id)
        for slot in uow.program_workouts.find_by_program(program_id):
            uow.program_workouts.delete(slot)
        uow.programs.delete(program)
        uow.commit()
        return CommandResult(status="deleted", id=program_id)

@register("activate_program")
class ActivateProgramHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        program_id = payload.get("id")
        if not program_id:
            return CommandResult(status="error", message="id is required")
        program = uow.programs.get_by_id(program_id)  # pyright: ignore[reportArgumentType]
        if not program:
            return CommandResult(status="not_found", id=program_id)
        if program.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", id=program_id)
        program.is_active = True
        uow.programs.update(program)
        uow.commit()
        return CommandResult(status="updated", record={"id": program_id, "is_active": True}, id=program_id)


@register("deactivate_program")
class DeactivateProgramHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        program_id = payload.get("id")
        if not program_id:
            return CommandResult(status="error", message="id is required")
        program = uow.programs.get_by_id(program_id)  # pyright: ignore[reportArgumentType]
        if not program:
            return CommandResult(status="not_found", id=program_id)
        if program.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", id=program_id)
        program.is_active = False
        uow.programs.update(program)
        uow.commit()
        return CommandResult(status="updated", record={"id": program_id, "is_active": False}, id=program_id)
