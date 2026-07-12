from datetime import datetime
from sqlmodel import select, or_, desc, col
from salus.models.workout import Exercise, WorkoutPlan, WorkoutSession, WorkoutLogEntry
from salus.repositories.base import Repository


class ExerciseRepository(Repository[Exercise]):
    model = Exercise

    def find_all_catalog(self, user_id: int) -> list[Exercise]:
        return list(
            self.session.exec(
                select(Exercise).where(
                    or_(Exercise.user_id == None, Exercise.user_id == user_id)  # type: ignore # noqa: E711
                )
            ).all()
        )

    def find_by_name(self, name: str) -> Exercise | None:
        return self.session.exec(select(Exercise).where(Exercise.name == name)).first()


class WorkoutPlanRepository(Repository[WorkoutPlan]):
    model = WorkoutPlan

    def find_by_user(self, user_id: int) -> list[WorkoutPlan]:
        return list(
            self.session.exec(
                select(WorkoutPlan)
                .where(WorkoutPlan.user_id == user_id)
                .order_by(WorkoutPlan.position, WorkoutPlan.created_at)  # pyright: ignore[reportArgumentType]
            ).all()
        )

    def reorder(self, user_id: int, ordered_ids: list[int]) -> None:
        for pos, plan_id in enumerate(ordered_ids):
            plan = self.get_by_id(plan_id)
            if plan is not None and plan.user_id == user_id:
                plan.position = pos
                self.session.add(plan)
        self.session.commit()


class WorkoutSessionRepository(Repository[WorkoutSession]):
    model = WorkoutSession

    def find_recent_by_user(
        self, user_id: int, limit: int = 10
    ) -> list[WorkoutSession]:
        return list(
            self.session.exec(
                select(WorkoutSession)
                .where(WorkoutSession.user_id == user_id)
                .order_by(desc(WorkoutSession.started_at))
                .limit(limit)
            ).all()
        )

    def find_all_by_user(self, user_id: int) -> list[WorkoutSession]:
        return list(
            self.session.exec(
                select(WorkoutSession).where(WorkoutSession.user_id == user_id)
            ).all()
        )

    def count_completed_in_range(
        self, user_id: int, since: datetime, until: datetime
    ) -> int:
        from sqlalchemy import func

        stmt = (
            select(func.count(WorkoutSession.id))  # type: ignore[arg-type]
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.completed_at >= since,  # type: ignore[operator]
                WorkoutSession.completed_at <= until,  # type: ignore[operator]
            )
        )
        result = self.session.exec(stmt).first()
        return int(result[0]) if result is not None and result[0] is not None else 0  # type: ignore[index]

    def find_completed_in_range(
        self, user_id: int, since: datetime, until: datetime
    ) -> list[WorkoutSession]:
        return list(
            self.session.exec(
                select(WorkoutSession)
                .where(
                    WorkoutSession.user_id == user_id,
                    WorkoutSession.completed_at.is_not(None),  # type: ignore[union-attr]
                    WorkoutSession.completed_at >= since,  # type: ignore[operator]
                    WorkoutSession.completed_at <= until,  # type: ignore[operator]
                )
                .order_by(WorkoutSession.completed_at.desc())  # type: ignore[union-attr]
            ).all()
        )

    def get_last_session_for_plan(
        self, user_id: int, plan_id: int
    ) -> WorkoutSession | None:
        return self.session.exec(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.plan_id == plan_id,
                WorkoutSession.completed_at != None,  # type: ignore # noqa: E711
            )
            .order_by(desc(WorkoutSession.completed_at))
            .limit(1)
        ).first()

    def get_personal_records(
        self, user_id: int, exercise_ids: list[int]
    ) -> dict[int, dict]:
        if not exercise_ids:
            return {}

        stmt = (
            select(WorkoutLogEntry)
            .join(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.completed_at != None,  # type: ignore # noqa: E711
                col(WorkoutLogEntry.exercise_id).in_(exercise_ids),
            )
        )
        entries = self.session.exec(stmt).all()

        results = {}
        for entry in entries:
            ex_id = entry.exercise_id
            if ex_id not in results:
                results[ex_id] = {"max_weight": 0.0, "max_est_1rm": 0.0}

            est_1rm = 0.0
            if entry.reps > 0:
                if entry.reps == 1:
                    est_1rm = entry.weight
                else:
                    est_1rm = entry.weight / (1.0278 - (0.0278 * entry.reps))

            results[ex_id]["max_weight"] = max(results[ex_id]["max_weight"], entry.weight)
            results[ex_id]["max_est_1rm"] = max(results[ex_id]["max_est_1rm"], est_1rm)

        return results
