from sqlmodel import select, or_, desc
from salus.models.workout import Exercise, WorkoutPlan, WorkoutSession
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
        return self.session.exec(
            select(Exercise).where(Exercise.name == name)
        ).first()


class WorkoutPlanRepository(Repository[WorkoutPlan]):
    model = WorkoutPlan

    def find_by_user(self, user_id: int) -> list[WorkoutPlan]:
        return list(
            self.session.exec(
                select(WorkoutPlan).where(WorkoutPlan.user_id == user_id)
            ).all()
        )


class WorkoutSessionRepository(Repository[WorkoutSession]):
    model = WorkoutSession

    def find_recent_by_user(self, user_id: int, limit: int = 10) -> list[WorkoutSession]:
        return list(
            self.session.exec(
                select(WorkoutSession)
                .where(WorkoutSession.user_id == user_id)
                .order_by(desc(WorkoutSession.started_at))
                .limit(limit)
            ).all()
        )

    def get_last_session_for_plan(self, user_id: int, plan_id: int) -> WorkoutSession | None:
        return self.session.exec(
            select(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutSession.plan_id == plan_id,
                WorkoutSession.completed_at != None  # type: ignore # noqa: E711
            )
            .order_by(desc(WorkoutSession.completed_at))
            .limit(1)
        ).first()
