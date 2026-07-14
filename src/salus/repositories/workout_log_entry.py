from sqlmodel import select
from sqlalchemy.orm import selectinload

from salus.models.workout import WorkoutLogEntry, WorkoutSession
from salus.repositories.base import Repository
from salus.repositories.protocols import IWorkoutLogEntryRepository


class WorkoutLogEntryRepository(Repository[WorkoutLogEntry], IWorkoutLogEntryRepository):
    model = WorkoutLogEntry

    def find_by_session_exercise_set(
        self, session_id: str, exercise_id: str, set_number: int
    ) -> WorkoutLogEntry | None:
        stmt = select(WorkoutLogEntry).where(
            WorkoutLogEntry.session_id == session_id,
            WorkoutLogEntry.exercise_id == exercise_id,
            WorkoutLogEntry.set_number == set_number,
        )
        return self.session.exec(stmt).first()

    def find_exercise_history(
        self, user_id: str, exercise_id: str
    ) -> list[WorkoutLogEntry]:
        stmt = (
            select(WorkoutLogEntry)
            .join(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutLogEntry.exercise_id == exercise_id,
                WorkoutSession.completed_at.is_not(None),  # type: ignore[union-attr]
            )
            .options(selectinload(WorkoutLogEntry.session))  # type: ignore[arg-type]
            .order_by(WorkoutSession.completed_at.desc())  # type: ignore[union-attr]
        )
        return list(self.session.exec(stmt).all())
