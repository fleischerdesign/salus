from datetime import datetime

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

    def get_exercise_progression(
        self,
        user_id: str,
        exercise_id: str,
        since: datetime | None = None,
    ) -> list[dict]:
        stmt = (
            select(WorkoutLogEntry)
            .join(WorkoutSession)
            .where(
                WorkoutSession.user_id == user_id,
                WorkoutLogEntry.exercise_id == exercise_id,
                WorkoutSession.completed_at.is_not(None),  # type: ignore[union-attr]
            )
            .options(selectinload(WorkoutLogEntry.session))  # type: ignore[arg-type]
            .order_by(WorkoutSession.completed_at.asc())  # type: ignore[union-attr]
        )
        if since is not None:
            stmt = stmt.where(WorkoutSession.completed_at >= since)  # type: ignore[operator]
        entries = list(self.session.exec(stmt).all())
        sessions: dict[str, dict[str, object]] = {}
        for entry in entries:
            s_date = entry.session.completed_at.strftime("%Y-%m-%d")  # type: ignore[union-attr]
            if s_date not in sessions:
                sessions[s_date] = {
                    "date": s_date,
                    "total_tonnage": 0.0,
                    "max_weight": 0.0,
                    "sets_count": 0,
                }
            tonnage = entry.weight * entry.reps
            sessions[s_date]["total_tonnage"] = float(sessions[s_date]["total_tonnage"]) + tonnage  # type: ignore[operator]
            sessions[s_date]["sets_count"] = int(sessions[s_date]["sets_count"]) + 1  # type: ignore[operator]
            sessions[s_date]["max_weight"] = max(  # type: ignore[operator, arg-type]
                float(sessions[s_date]["max_weight"]), entry.weight  # type: ignore[operator, arg-type]
            )
        return list(sessions.values())
