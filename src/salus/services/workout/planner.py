from typing import Optional

from salus.exceptions import NotFoundError
from salus.services.constants import DEFAULT_REST_SECONDS
from salus.models.workout import Exercise, Program, Workout, WorkoutSet, WorkoutSession
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.workout.autoregulation import AutoregulationService
from salus.services.workout.progression import (
    AutoregulatedProgressionScheme,
    LinearProgressionScheme,
    NoneProgressionScheme,
    ProgressionContext,
    ProgressionScheme,
)


class WorkoutService:
    """Read-only workout queries (write path is command handlers)."""

    def __init__(self, uow: IUnitOfWork, autoreg_svc: AutoregulationService) -> None:
        self.uow = uow
        self.autoreg_svc = autoreg_svc
        self._schemes: dict[str, ProgressionScheme] = {
            "none": NoneProgressionScheme(),
            "linear": LinearProgressionScheme(),
            "autoregulated": AutoregulatedProgressionScheme(autoreg_svc),
        }

    # --------------------------------------------------------------------------
    # Exercise reads
    # --------------------------------------------------------------------------

    def get_exercise_catalog(self, user_id: str) -> list[Exercise]:
        with self.uow:
            return self.uow.exercises.find_all_catalog(user_id)

    def get_exercise(self, user_id: str, exercise_id: str) -> Optional[Exercise]:
        with self.uow:
            ex = self.uow.exercises.get_by_id(exercise_id)
            if ex and (ex.user_id is None or ex.user_id == user_id):
                return ex
            return None

    # --------------------------------------------------------------------------
    # Plan reads
    # --------------------------------------------------------------------------

    def get_workout(self, user_id: str, workout_id: str) -> Workout:
        with self.uow:
            workout = self.uow.workouts.get_by_id(workout_id)
            if not workout or workout.user_id != user_id:
                raise NotFoundError("Workout not found.")
            return workout

    def list_workouts(self, user_id: str) -> list[Workout]:
        with self.uow:
            return self.uow.workouts.find_by_user(user_id)

    # --------------------------------------------------------------------------
    # Program reads
    # --------------------------------------------------------------------------

    def list_programs(self, user_id: str) -> list[Program]:
        with self.uow:
            return self.uow.programs.find_by_user(user_id)

    def get_program(self, user_id: str, program_id: str) -> Program:
        with self.uow:
            program = self.uow.programs.get_by_id(program_id)
            if not program or program.user_id != user_id:
                raise NotFoundError("Program not found.")
            return program

    # --------------------------------------------------------------------------
    # Session reads
    # --------------------------------------------------------------------------

    def get_active_session(self, user_id: str) -> Optional[WorkoutSession]:
        with self.uow:
            return self.uow.workout_sessions.find_active_by_user(user_id)

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
        self,
        user_id: str,
        workout_id: str,
        date_str: Optional[str] = None,
        progression_scheme: str = "autoregulated",
    ) -> list[dict]:
        with self.uow:
            workout = self.uow.workouts.get_by_id(workout_id)
            if not workout or workout.user_id != user_id:
                raise NotFoundError("Workout not found.")

            # Resolve exercises
            exercises_with_targets = []
            for workout_ex in workout.exercises:
                ex = self.uow.exercises.get_by_id(workout_ex.exercise_id)
                if ex:
                    exercises_with_targets.append((workout_ex, ex))

            last_sess = self.uow.workout_sessions.get_last_session_for_workout(user_id, workout_id)
            last_weights: dict[str, float] = {}
            last_reps: dict[str, int] = {}
            last_rpes: dict[str, float | None] = {}
            if last_sess:
                for entry in last_sess.sets:
                    if entry.weight >= last_weights.get(entry.exercise_id, 0.0):
                        last_weights[entry.exercise_id] = entry.weight
                        last_reps[entry.exercise_id] = entry.reps
                        last_rpes[entry.exercise_id] = entry.rpe

            ctx = ProgressionContext(
                user_id=user_id,
                date_str=date_str,
                exercises=exercises_with_targets,
                last_weights=last_weights,
                last_reps=last_reps,
                last_rpes=last_rpes,
            )
            scheme = self._schemes.get(progression_scheme, self._schemes["autoregulated"])
            targets = scheme.compute_targets(ctx)

            exercise_ids = [t["exercise_id"] for t in targets]
            prs = self.uow.workout_sessions.get_personal_records(user_id, exercise_ids)

            # Map exercise ID to workout/exercise objects for rest duration resolution
            workout_ex_map = {pe.exercise_id: (pe, e) for pe, e in exercises_with_targets}

            for t in targets:
                t["last_weight"] = last_weights.get(t["exercise_id"], None)
                ex_pr = prs.get(t["exercise_id"], {})
                t["pr_weight"] = ex_pr.get("max_weight", 0.0)
                t["pr_est_1rm"] = ex_pr.get("max_est_1rm", 0.0)

                # Resolve rest duration override or default
                pe, e = workout_ex_map.get(t["exercise_id"], (None, None))
                rest_val = pe.rest_seconds if pe else None
                if rest_val is None and e:
                    rest_val = e.suggested_rest_seconds
                t["rest_seconds"] = rest_val if rest_val is not None else DEFAULT_REST_SECONDS

            return targets

    def get_exercise_history(self, user_id: str, exercise_id: str) -> list[WorkoutSet]:
        with self.uow:
            return self.uow.workout_sets.find_exercise_history(
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

    def get_workout_history(self, user_id: str, workout_id: str) -> list[WorkoutSession]:
        with self.uow:
            return self.uow.workout_sessions.find_completed_by_workout(
                user_id, workout_id
            )

    def get_workout_details(self, user_id: str, workout_id: str) -> dict:
        with self.uow:
            workout = self.uow.workouts.get_by_id(workout_id)
            if not workout or workout.user_id != user_id:
                raise NotFoundError("Workout not found.")

            exercises_with_details = []
            for workout_ex in workout.exercises:
                ex = self.uow.exercises.get_by_id(workout_ex.exercise_id)
                if ex:
                    exercises_with_details.append({
                        "workout_exercise": workout_ex,
                        "exercise": ex
                    })

            history = self.get_workout_history(user_id, workout_id)

            return {
                "workout": workout,
                "exercises": exercises_with_details,
                "history": history
            }
