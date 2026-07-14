from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from salus.models.workout import Exercise, WorkoutLogEntry, WorkoutPlan, WorkoutPlanExercise, WorkoutSession
from salus.services._helpers import uuid7_str
from salus.services.command_registry import CommandResult, register

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User


def _new_uuid() -> str:
    return uuid7_str()


def _serialize_session(session: WorkoutSession) -> dict[str, Any]:
    from datetime import datetime as dt

    def _fmt(v: Any) -> Any:
        if isinstance(v, dt):
            return v.replace(tzinfo=None).isoformat() if v.tzinfo else v.isoformat()
        return v

    result: dict[str, Any] = {}
    for k in ("id", "user_id", "plan_id", "started_at", "completed_at",
              "autoreg_mode", "recovery_score", "notes", "created_at", "updated_at", "deleted_at"):
        if hasattr(session, k):
            result[k] = _fmt(getattr(session, k))
    return result


def _serialize_log_entry(entry: WorkoutLogEntry) -> dict[str, Any]:
    from datetime import datetime as dt

    def _fmt(v: Any) -> Any:
        if isinstance(v, dt):
            return v.replace(tzinfo=None).isoformat() if v.tzinfo else v.isoformat()
        return v

    result: dict[str, Any] = {}
    for k in ("id", "session_id", "exercise_id", "set_number", "weight", "reps",
              "rpe", "created_at", "updated_at", "deleted_at"):
        if hasattr(entry, k):
            result[k] = _fmt(getattr(entry, k))
    return result


@register("start_workout")
class StartWorkoutHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        plan_id = payload.get("plan_id")
        session_id = payload.get("id")

        active = uow.workout_sessions.find_active_by_user(user.id)  # pyright: ignore[reportArgumentType]
        if active:
            return CommandResult(status="created", record=_serialize_session(active), id=active.id)

        autoreg_mode = "advisory"
        recovery_score = None
        if plan_id:
            plan = uow.workout_plans.get_by_id(plan_id)
            if plan and plan.user_id == user.id:  # pyright: ignore[reportAttributeAccessIssue]
                autoreg_mode = plan.autoreg_mode
                if autoreg_mode != "disabled":
                    recovery_score = self._calculate_recovery(uow, user)

        now = datetime.now(timezone.utc)
        session = WorkoutSession(
            id=session_id,
            user_id=user.id,  # pyright: ignore[reportArgumentType]
            plan_id=plan_id,
            started_at=now,
            autoreg_mode=autoreg_mode,
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
        from salus.services._helpers import uid
        from salus.services.analytics.sleep import SleepAnalysisService
        from salus.services.analytics.activity import ActivityAnalysisService
        from salus.services.workout.autoregulation import AutoregulationService

        user_id = uid(user)
        sleep_svc = SleepAnalysisService(uow.measurements)
        activity_svc = ActivityAnalysisService(uow.measurements)
        autoreg_svc = AutoregulationService(sleep_svc, activity_svc)
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
        entry = WorkoutLogEntry(
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
        uow.workout_log_entries.add(entry)
        uow.commit()
        uow.session.refresh(entry)
        return CommandResult(status="created", record=_serialize_log_entry(entry), id=entry.id)

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
            return CommandResult(status="error", message="id is required")

        from sqlmodel import select

        stmt = select(WorkoutLogEntry).where(WorkoutLogEntry.id == entry_id)
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


@register("create_exercise")
class CreateExerciseHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        name = payload.get("name", "").strip()
        existing = uow.exercises.find_by_name(name)
        if existing:
            return CommandResult(status="error", message=f"Exercise '{name}' already exists")

        now = datetime.now(timezone.utc)
        ex = Exercise(
            id=payload.get("id"),
            name=name,
            equipment=payload.get("equipment", "barbell"),
            primary_muscles=payload.get("primary_muscles", ""),
            secondary_muscles=payload.get("secondary_muscles"),
            description=payload.get("description"),
            instructions=payload.get("instructions"),
            video_url=payload.get("video_url"),
            image_url=payload.get("image_url"),
            user_id=user.id,
            created_at=now,
            updated_at=now,
        )
        uow.exercises.add(ex)
        uow.commit()
        uow.session.refresh(ex)

        record: dict[str, Any] = {k: getattr(ex, k, None) for k in
            ("id", "name", "equipment", "primary_muscles", "secondary_muscles",
             "description", "instructions", "video_url", "image_url", "user_id")}
        return CommandResult(status="created", record=record, id=ex.id)


@register("delete_exercise")
class DeleteExerciseHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        ex_id = payload.get("id")
        if not ex_id:
            return CommandResult(status="error", message="id is required")
        ex = uow.exercises.get_by_id(ex_id)  # pyright: ignore[reportArgumentType]
        if not ex:
            return CommandResult(status="deleted", id=ex_id)
        if ex.user_id is not None and ex.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", message="Cannot delete system exercise")
        uow.exercises.delete(ex)
        uow.commit()
        return CommandResult(status="deleted", id=ex_id)


@register("create_plan")
class CreatePlanHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        name = payload.get("name", "").strip()
        if not name:
            return CommandResult(status="error", message="name is required")

        now = datetime.now(timezone.utc)
        plan_id = payload.get("id") or _new_uuid()
        plan = WorkoutPlan(
            id=plan_id,
            name=name,
            description=payload.get("description"),
            user_id=user.id,  # pyright: ignore[reportArgumentType]
            autoreg_mode=payload.get("autoreg_mode", "advisory"),
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
            plan_ex = WorkoutPlanExercise(
                id=item.get("id"),
                plan_id=plan_id,
                exercise_id=exercise_id,
                sequence=item.get("sequence", 0),
                target_sets=item.get("target_sets", 3),
                target_reps=item.get("target_reps", 8),
                target_rpe=item.get("target_rpe", 8.0),
                is_autoreg_exempt=item.get("is_autoreg_exempt", False),
                rest_seconds=item.get("rest_seconds"),
                created_at=now,
                updated_at=now,
            )
            uow.workout_plan_exercises.add(plan_ex)
        uow.workout_plans.add(plan)
        uow.commit()

        record: dict[str, Any] = {"id": plan_id, "name": plan.name,
            "description": plan.description, "autoreg_mode": plan.autoreg_mode}
        return CommandResult(status="created", record=record, id=plan_id)


@register("delete_plan")
class DeletePlanHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        plan_id = payload.get("id")
        if not plan_id:
            return CommandResult(status="error", message="id is required")
        plan = uow.workout_plans.get_by_id(plan_id)  # pyright: ignore[reportArgumentType]
        if not plan:
            return CommandResult(status="deleted", id=plan_id)
        if plan.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", id=plan_id)
        uow.workout_plans.delete(plan)
        uow.commit()
        return CommandResult(status="deleted", id=plan_id)