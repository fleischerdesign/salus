from datetime import datetime, timezone
from typing import Optional
from salus.exceptions import NotFoundError
from salus.models.workout import (
    Exercise,
    WorkoutPlan,
    WorkoutPlanExercise,
    WorkoutSession,
    WorkoutLogEntry,
)
from salus.schemas.workout import (
    ExerciseCreate,
    WorkoutPlanCreate,
    WorkoutLogEntryCreate,
)
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.workout.autoregulation import AutoregulationService


class WorkoutService:
    def __init__(self, uow: IUnitOfWork, autoreg_svc: AutoregulationService) -> None:
        self.uow = uow
        self.autoreg_svc = autoreg_svc

    # --------------------------------------------------------------------------
    # Exercise CRUD
    # --------------------------------------------------------------------------

    def create_exercise(self, user_id: int, data: ExerciseCreate) -> Exercise:
        with self.uow:
            # Check if name is taken
            existing = self.uow.exercises.find_by_name(data.name)
            if existing:
                raise ValueError(f"Exercise with name '{data.name}' already exists.")

            ex = Exercise(
                name=data.name,
                equipment=data.equipment,
                primary_muscles=data.primary_muscles,
                secondary_muscles=data.secondary_muscles,
                description=data.description,
                instructions=data.instructions,
                video_url=data.video_url,
                image_url=data.image_url,
                user_id=user_id,
            )
            self.uow.exercises.add(ex)
            self.uow.commit()
            return ex

    def update_exercise(self, user_id: int, exercise_id: int, data: ExerciseCreate) -> Exercise:
        with self.uow:
            ex = self.uow.exercises.get_by_id(exercise_id)
            if not ex:
                raise NotFoundError("Exercise not found.")
            if ex.user_id != user_id:
                raise PermissionError("Cannot edit system default exercise.")

            # Check if name is taken by another exercise
            existing = self.uow.exercises.find_by_name(data.name)
            if existing and existing.id != exercise_id:
                raise ValueError(f"Exercise with name '{data.name}' already exists.")

            ex.name = data.name
            ex.equipment = data.equipment
            ex.primary_muscles = data.primary_muscles
            ex.secondary_muscles = data.secondary_muscles
            ex.description = data.description
            ex.instructions = data.instructions
            ex.video_url = data.video_url
            self.uow.commit()
            return ex

    def get_exercise_catalog(self, user_id: int) -> list[Exercise]:
        with self.uow:
            return self.uow.exercises.find_all_catalog(user_id)

    def get_exercise(self, user_id: int, exercise_id: int) -> Optional[Exercise]:
        with self.uow:
            ex = self.uow.exercises.get_by_id(exercise_id)
            if ex and (ex.user_id is None or ex.user_id == user_id):
                return ex
            return None

    def delete_exercise(self, user_id: int, exercise_id: int) -> None:
        with self.uow:
            ex = self.uow.exercises.get_by_id(exercise_id)
            if not ex:
                raise NotFoundError("Exercise not found.")
            if ex.user_id != user_id:
                raise PermissionError("Cannot delete system default exercise.")
            self.uow.exercises.delete(ex)
            self.uow.commit()

    # --------------------------------------------------------------------------
    # Plan CRUD
    # --------------------------------------------------------------------------

    def create_plan(self, user_id: int, data: WorkoutPlanCreate) -> WorkoutPlan:
        with self.uow:
            plan = WorkoutPlan(
                name=data.name,
                description=data.description,
                user_id=user_id,
                autoreg_mode=data.autoreg_mode,
            )
            self.uow.workout_plans.add(plan)
            self.uow.commit()

            # Add plan exercises
            from typing import cast
            from salus.repositories.unit_of_work import SqlUnitOfWork

            sql_uow = cast(SqlUnitOfWork, self.uow)

            plan_id = plan.id
            if plan_id is None:
                raise ValueError("Plan was not persisted correctly.")

            for item in data.exercises:
                ex = self.uow.exercises.get_by_id(item.exercise_id)
                if not ex:
                    raise NotFoundError(f"Exercise ID {item.exercise_id} not found.")

                plan_ex = WorkoutPlanExercise(
                    plan_id=plan_id,
                    exercise_id=item.exercise_id,
                    sequence=item.sequence,
                    target_sets=item.target_sets,
                    target_reps=item.target_reps,
                    target_rpe=item.target_rpe,
                    is_autoreg_exempt=item.is_autoreg_exempt,
                )
                sql_uow.session.add(plan_ex)

            self.uow.commit()
            return plan

    def get_plan(self, user_id: int, plan_id: int) -> WorkoutPlan:
        with self.uow:
            plan = self.uow.workout_plans.get_by_id(plan_id)
            if not plan or plan.user_id != user_id:
                raise NotFoundError("Workout plan not found.")
            return plan

    def list_plans(self, user_id: int) -> list[WorkoutPlan]:
        with self.uow:
            return self.uow.workout_plans.find_by_user(user_id)

    def reorder_plans(self, user_id: int, ordered_ids: list[int]) -> None:
        with self.uow:
            self.uow.workout_plans.reorder(user_id, ordered_ids)
            self.uow.commit()

    def update_plan(self, user_id: int, plan_id: int, data: WorkoutPlanCreate) -> WorkoutPlan:
        with self.uow:
            plan = self.uow.workout_plans.get_by_id(plan_id)
            if not plan or plan.user_id != user_id:
                raise NotFoundError("Workout plan not found.")

            plan.name = data.name
            plan.description = data.description
            plan.autoreg_mode = data.autoreg_mode
            self.uow.workout_plans.update(plan)

            # Replace plan exercises
            from typing import cast
            from salus.repositories.unit_of_work import SqlUnitOfWork
            from sqlmodel import select
            
            sql_uow = cast(SqlUnitOfWork, self.uow)

            # Delete old plan exercises
            stmt = select(WorkoutPlanExercise).where(WorkoutPlanExercise.plan_id == plan_id)
            old_exercises = sql_uow.session.exec(stmt).all()
            for old_ex in old_exercises:
                sql_uow.session.delete(old_ex)
            sql_uow.session.flush()

            # Add new plan exercises
            for item in data.exercises:
                ex = self.uow.exercises.get_by_id(item.exercise_id)
                if not ex:
                    raise NotFoundError(f"Exercise ID {item.exercise_id} not found.")

                plan_ex = WorkoutPlanExercise(
                    plan_id=plan_id,
                    exercise_id=item.exercise_id,
                    sequence=item.sequence,
                    target_sets=item.target_sets,
                    target_reps=item.target_reps,
                    target_rpe=item.target_rpe,
                    is_autoreg_exempt=item.is_autoreg_exempt,
                )
                sql_uow.session.add(plan_ex)

            self.uow.commit()
            return plan

    def delete_plan(self, user_id: int, plan_id: int) -> None:
        with self.uow:
            plan = self.uow.workout_plans.get_by_id(plan_id)
            if not plan or plan.user_id != user_id:
                raise NotFoundError("Workout plan not found.")
            self.uow.workout_plans.delete(plan)
            self.uow.commit()

    # --------------------------------------------------------------------------
    # Workout Sessions Logging
    # --------------------------------------------------------------------------

    def start_session(
        self, user_id: int, plan_id: Optional[int] = None
    ) -> WorkoutSession:
        with self.uow:
            # Check for active session
            active = self.get_active_session(user_id)
            if active:
                return active

            autoreg_mode = "disabled"
            recovery_score = None
            if plan_id:
                plan = self.uow.workout_plans.get_by_id(plan_id)
                if plan and plan.user_id == user_id:
                    autoreg_mode = plan.autoreg_mode
                    if autoreg_mode != "disabled":
                        scores = self.autoreg_svc.calculate_recovery_score(user_id)
                        recovery_score = scores[0]

            session = WorkoutSession(
                user_id=user_id,
                plan_id=plan_id,
                started_at=datetime.now(timezone.utc),
                autoreg_mode=autoreg_mode,
                recovery_score=recovery_score,
            )
            self.uow.workout_sessions.add(session)
            self.uow.commit()
            return session

    def get_active_session(self, user_id: int) -> Optional[WorkoutSession]:
        with self.uow:
            from sqlmodel import select
            from sqlalchemy.orm import selectinload
            from typing import cast, Any
            from salus.repositories.unit_of_work import SqlUnitOfWork

            sql_uow = cast(SqlUnitOfWork, self.uow)

            stmt = (
                select(WorkoutSession)
                .where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.completed_at.is_(None),  # type: ignore # noqa: E711
                )
                .options(selectinload(cast(Any, WorkoutSession.logs)))
            )
            return sql_uow.session.exec(stmt).first()

    def log_set(
        self, user_id: int, session_id: int, entry: WorkoutLogEntryCreate
    ) -> WorkoutLogEntry:
        with self.uow:
            session = self.uow.workout_sessions.get_by_id(session_id)
            if not session or session.user_id != user_id:
                raise NotFoundError("Active workout session not found.")

            log = WorkoutLogEntry(
                session_id=session_id,
                exercise_id=entry.exercise_id,
                set_number=entry.set_number,
                weight=entry.weight,
                reps=entry.reps,
                rpe=entry.rpe,
            )
            from typing import cast
            from salus.repositories.unit_of_work import SqlUnitOfWork

            sql_uow = cast(SqlUnitOfWork, self.uow)
            sql_uow.session.add(log)
            self.uow.commit()
            return log

    def delete_logged_set(
        self, user_id: int, session_id: int, exercise_id: int, set_number: int
    ) -> None:
        with self.uow:
            session = self.uow.workout_sessions.get_by_id(session_id)
            if not session or session.user_id != user_id:
                raise NotFoundError("Workout session not found.")

            from sqlmodel import select
            from salus.models.workout import WorkoutLogEntry
            from typing import cast
            from salus.repositories.unit_of_work import SqlUnitOfWork

            sql_uow = cast(SqlUnitOfWork, self.uow)
            stmt = (
                select(WorkoutLogEntry)
                .where(WorkoutLogEntry.session_id == session_id)
                .where(WorkoutLogEntry.exercise_id == exercise_id)
                .where(WorkoutLogEntry.set_number == set_number)
            )
            entry = sql_uow.session.exec(stmt).first()
            if entry:
                sql_uow.session.delete(entry)
                self.uow.commit()

    def complete_session(
        self, user_id: int, session_id: int, notes: Optional[str] = None
    ) -> WorkoutSession:
        with self.uow:
            session = self.uow.workout_sessions.get_by_id(session_id)
            if not session or session.user_id != user_id:
                raise NotFoundError("Workout session not found.")

            session.completed_at = datetime.now(timezone.utc)
            if notes is not None:
                session.notes = notes
            self.uow.workout_sessions.update(session)
            self.uow.commit()
            return session

    def get_recent_sessions(
        self, user_id: int, limit: int = 10
    ) -> list[WorkoutSession]:
        with self.uow:
            return self.uow.workout_sessions.find_recent_by_user(user_id, limit)

    def get_session(self, user_id: int, session_id: int) -> Optional[WorkoutSession]:
        with self.uow as sql_uow:
            from sqlalchemy.orm import selectinload
            from sqlmodel import select
            from typing import Any, cast

            stmt = (
                select(WorkoutSession)
                .where(WorkoutSession.user_id == user_id)
                .where(WorkoutSession.id == session_id)
                .options(
                    selectinload(cast(Any, WorkoutSession.logs)),
                    selectinload(cast(Any, WorkoutSession.plan))
                )
            )
            return sql_uow.session.exec(stmt).first()

    def get_session_targets(
        self, user_id: int, plan_id: int, date_str: Optional[str] = None
    ) -> list[dict]:
        with self.uow:
            plan = self.uow.workout_plans.get_by_id(plan_id)
            if not plan or plan.user_id != user_id:
                raise NotFoundError("Workout plan not found.")

            # Resolve exercises
            exercises_with_targets = []
            for plan_ex in plan.plan_exercises:
                ex = self.uow.exercises.get_by_id(plan_ex.exercise_id)
                if ex:
                    exercises_with_targets.append((plan_ex, ex))

            last_sess = self.uow.workout_sessions.get_last_session_for_plan(user_id, plan_id)
            last_weights = {}
            if last_sess:
                for entry in last_sess.logs:
                    last_weights[entry.exercise_id] = max(
                        last_weights.get(entry.exercise_id, 0.0), entry.weight
                    )

            if plan.autoreg_mode == "disabled":
                # Return standard targets directly
                targets = [
                    {
                        "exercise_id": ex.id,
                        "name": ex.name,
                        "suggested_sets": plan_ex.target_sets,
                        "suggested_reps": plan_ex.target_reps,
                        "suggested_rpe": plan_ex.target_rpe or 8.0,
                        "weight_multiplier": 1.0,
                        "is_autoreg_exempt": True,
                        "reason": "Autoregulation disabled for this plan.",
                    }
                    for plan_ex, ex in exercises_with_targets
                ]
            else:
                targets = self.autoreg_svc.get_autoregulated_targets(
                    user_id=user_id,
                    exercises_with_targets=exercises_with_targets,
                    date_str=date_str,
                )

            exercise_ids = [t["exercise_id"] for t in targets]
            prs = self.uow.workout_sessions.get_personal_records(user_id, exercise_ids)

            for t in targets:
                t["last_weight"] = last_weights.get(t["exercise_id"], None)
                ex_pr = prs.get(t["exercise_id"], {})
                t["pr_weight"] = ex_pr.get("max_weight", 0.0)
                t["pr_est_1rm"] = ex_pr.get("max_est_1rm", 0.0)

            return targets
