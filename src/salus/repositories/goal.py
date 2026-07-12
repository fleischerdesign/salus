from sqlmodel import select

from salus.models.goal import Goal
from salus.repositories.base import Repository


class GoalRepository(Repository[Goal]):
    model = Goal

    def find_by_user(self, user_id: int) -> list[Goal]:
        return list(
            self.session.exec(
                select(Goal).where(Goal.user_id == user_id, Goal.is_active, Goal.deleted_at.is_(None))  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_all_goals(self) -> list[Goal]:
        return list(self.session.exec(select(Goal)).all())
