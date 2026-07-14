from datetime import datetime, timezone
from typing import Optional
from salus.exceptions import ForbiddenError, NotFoundError
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

    def create_exercise(self, user_id: str, data: ExerciseCreate) -> Exercise:
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

    def update_exercise(self, user_id: str, exercise_id: str, data: ExerciseCreate) -> Exercise:
        with self.uow:
            ex = self.uow.exercises.get_by_id(exercise_id)
            if not ex:
                raise NotFoundError("Exercise not found.")
            if ex.user_id != user_id:
                raise ForbiddenError("Cannot edit system default exercise.")

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

    def get_exercise_catalog(self, user_id: str) -> list[Exercise]:
        with self.uow:
            return self.uow.exercises.find_all_catalog(user_id)

    def get_exercise(self, user_id: str, exercise_id: str) -> Optional[Exercise]:
        with self.uow:
            ex = self.uow.exercises.get_by_id(exercise_id)
            if ex and (ex.user_id is None or ex.user_id == user_id):
                return ex
            return None

    def delete_exercise(self, user_id: str, exercise_id: str) -> None:
        with self.uow:
            ex = self.uow.exercises.get_by_id(exercise_id)
            if not ex:
                raise NotFoundError("Exercise not found.")
            if ex.user_id != user_id:
                raise ForbiddenError("Cannot delete system default exercise.")
            self.uow.exercises.delete(ex)
            self.uow.commit()

    # --------------------------------------------------------------------------
    # Plan CRUD
    # --------------------------------------------------------------------------

    def create_plan(self, user_id: str, data: WorkoutPlanCreate) -> WorkoutPlan:
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
                    rest_seconds=item.rest_seconds,
                )
                self.uow.workout_plan_exercises.add(plan_ex)

            self.uow.commit()
            return plan

    def get_plan(self, user_id: str, plan_id: str) -> WorkoutPlan:
        with self.uow:
            plan = self.uow.workout_plans.get_by_id(plan_id)
            if not plan or plan.user_id != user_id:
                raise NotFoundError("Workout plan not found.")
            return plan

    def list_plans(self, user_id: str) -> list[WorkoutPlan]:
        with self.uow:
            return self.uow.workout_plans.find_by_user(user_id)

    def reorder_plans(self, user_id: str, ordered_ids: list[str]) -> None:
        with self.uow:
            self.uow.workout_plans.reorder(user_id, ordered_ids)
            self.uow.commit()

    def update_plan(
        self,
        user_id: str,
        plan_id: str,
        data: WorkoutPlanCreate,
        client_updated_at: Optional[datetime] = None,
    ) -> WorkoutPlan:
        with self.uow:
            plan = self.uow.workout_plans.get_by_id(plan_id)
            if not plan or plan.user_id != user_id:
                raise NotFoundError("Workout plan not found.")

            if client_updated_at is not None and plan.updated_at is not None:
                client_naive = client_updated_at.replace(tzinfo=None) if client_updated_at.tzinfo else client_updated_at
                plan_naive = plan.updated_at.replace(tzinfo=None) if plan.updated_at.tzinfo else plan.updated_at
                if plan_naive > client_naive:
                    from salus.exceptions import ConflictError
                    raise ConflictError(
                        "Workout plan was modified online. Stale offline update rejected."
                    )

            plan.name = data.name
            plan.description = data.description
            plan.autoreg_mode = data.autoreg_mode
            self.uow.workout_plans.update(plan)

            # Replace plan exercises
            plan_pk = plan.id
            if plan_pk is None:
                raise ValueError("Plan was not persisted correctly.")

            new_exercises = []
            for item in data.exercises:
                ex = self.uow.exercises.get_by_id(item.exercise_id)
                if not ex:
                    raise NotFoundError(f"Exercise ID {item.exercise_id} not found.")

                plan_ex = WorkoutPlanExercise(
                    plan_id=plan_pk,
                    exercise_id=item.exercise_id,
                    sequence=item.sequence,
                    target_sets=item.target_sets,
                    target_reps=item.target_reps,
                    target_rpe=item.target_rpe,
                    is_autoreg_exempt=item.is_autoreg_exempt,
                    rest_seconds=item.rest_seconds,
                )
                new_exercises.append(plan_ex)

            self.uow.workout_plan_exercises.replace_exercises_for_plan(
                plan_pk, new_exercises
            )

            self.uow.commit()
            return plan

    def delete_plan(self, user_id: str, plan_id: str) -> None:
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
        self, user_id: str, plan_id: Optional[str] = None
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

    def get_active_session(self, user_id: str) -> Optional[WorkoutSession]:
        with self.uow:
            return self.uow.workout_sessions.find_active_by_user(user_id)

    def log_set(
        self, user_id: str, session_id: str, entry: WorkoutLogEntryCreate
    ) -> WorkoutLogEntry:
        with self.uow:
            if not session_id or session_id in ("0", "active"):
                session = self.get_active_session(user_id)
                if not session:
                    raise NotFoundError("No active workout session found for this user.")
                if session.id is None:
                    raise ValueError("Workout session has no persisted ID")
                session_id = session.id
            else:
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
            self.uow.workout_log_entries.add(log)
            self.uow.commit()
            return log

    def delete_logged_set(
        self, user_id: str, session_id: str, exercise_id: str, set_number: int
    ) -> None:
        with self.uow:
            if not session_id or session_id in ("0", "active"):
                session = self.get_active_session(user_id)
                if not session:
                    raise NotFoundError("No active workout session found for this user.")
                if session.id is None:
                    raise ValueError("Workout session has no persisted ID")
                session_id = session.id
            else:
                session = self.uow.workout_sessions.get_by_id(session_id)
                if not session or session.user_id != user_id:
                    raise NotFoundError("Workout session not found.")

            entry = self.uow.workout_log_entries.find_by_session_exercise_set(
                session_id, exercise_id, set_number
            )
            if entry:
                self.uow.session.delete(entry)
                self.uow.commit()

    def complete_session(
        self, user_id: str, session_id: str, notes: Optional[str] = None
    ) -> WorkoutSession:
        with self.uow:
            if not session_id or session_id in ("0", "active"):
                session = self.get_active_session(user_id)
                if not session:
                    raise NotFoundError("No active workout session found for this user.")
                if session.id is None:
                    raise ValueError("Workout session has no persisted ID")
                session_id = session.id
            else:
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
        self, user_id: str, limit: int = 10
    ) -> list[WorkoutSession]:
        with self.uow:
            return self.uow.workout_sessions.find_recent_by_user(user_id, limit)

    def get_session(self, user_id: str, session_id: str) -> Optional[WorkoutSession]:
        with self.uow:
            return self.uow.workout_sessions.get_by_id_with_relations(
                session_id, user_id
            )

    def get_session_targets(
        self, user_id: str, plan_id: str, date_str: Optional[str] = None
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

            # Map exercise ID to plan/exercise objects for rest duration resolution
            plan_ex_map = {pe.exercise_id: (pe, e) for pe, e in exercises_with_targets}

            for t in targets:
                t["last_weight"] = last_weights.get(t["exercise_id"], None)
                ex_pr = prs.get(t["exercise_id"], {})
                t["pr_weight"] = ex_pr.get("max_weight", 0.0)
                t["pr_est_1rm"] = ex_pr.get("max_est_1rm", 0.0)
                
                # Resolve rest duration override or default
                pe, e = plan_ex_map.get(t["exercise_id"], (None, None))
                rest_val = pe.rest_seconds if pe else None
                if rest_val is None and e:
                    rest_val = e.suggested_rest_seconds
                t["rest_seconds"] = rest_val if rest_val is not None else 90

            return targets

    def get_exercise_history(self, user_id: str, exercise_id: str) -> list[WorkoutLogEntry]:
        with self.uow:
            return self.uow.workout_log_entries.find_exercise_history(
                user_id, exercise_id
            )

    def get_exercise_details(self, user_id: str, exercise_id: str) -> dict:
        with self.uow:
            exercise = self.get_exercise(user_id, exercise_id)
            if not exercise:
                raise NotFoundError("Exercise not found.")
                
            history = self.get_exercise_history(user_id, exercise_id)
            prs = self.uow.workout_sessions.get_personal_records(user_id, [exercise_id])
            ex_pr = prs.get(exercise_id, {})
            pr_weight = ex_pr.get("max_weight", 0.0)
            pr_est_1rm = ex_pr.get("max_est_1rm", 0.0)
            
            return {
                "exercise": exercise,
                "history": history,
                "pr_weight": pr_weight,
                "pr_est_1rm": pr_est_1rm
            }

    def get_plan_history(self, user_id: str, plan_id: str) -> list[WorkoutSession]:
        with self.uow:
            return self.uow.workout_sessions.find_completed_by_plan(
                user_id, plan_id
            )

    def get_plan_details(self, user_id: str, plan_id: str) -> dict:
        with self.uow:
            plan = self.uow.workout_plans.get_by_id(plan_id)
            if not plan or plan.user_id != user_id:
                raise NotFoundError("Workout plan not found.")
                
            exercises_with_details = []
            for plan_ex in plan.plan_exercises:
                ex = self.uow.exercises.get_by_id(plan_ex.exercise_id)
                if ex:
                    exercises_with_details.append({
                        "plan_exercise": plan_ex,
                        "exercise": ex
                    })
                    
            history = self.get_plan_history(user_id, plan_id)
            
            return {
                "plan": plan,
                "exercises": exercises_with_details,
                "history": history
            }
