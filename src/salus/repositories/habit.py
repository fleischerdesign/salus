from datetime import date

from sqlmodel import select

from salus.models.habit import Habit, HabitLog
from salus.repositories.base import Repository


class HabitRepository(Repository[Habit]):
    model = Habit

    def find_by_user(self, user_id: str) -> list[Habit]:
        return list(
            self.session.exec(
                select(Habit).where(
                    Habit.user_id == user_id,
                    Habit.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
            ).all()
        )

    def find_active(self, user_id: str) -> list[Habit]:
        return list(
            self.session.exec(
                select(Habit).where(
                    Habit.user_id == user_id,
                    Habit.is_archived == False,  # noqa: E712
                    Habit.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
            ).all()
        )


class HabitLogRepository(Repository[HabitLog]):
    model = HabitLog

    def find_by_habit(self, habit_id: str) -> list[HabitLog]:
        return list(
            self.session.exec(
                select(HabitLog).where(
                    HabitLog.habit_id == habit_id,
                    HabitLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(HabitLog.log_date.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_habit_and_user(self, habit_id: str, user_id: str) -> list[HabitLog]:
        return list(
            self.session.exec(
                select(HabitLog).where(
                    HabitLog.habit_id == habit_id,
                    HabitLog.user_id == user_id,
                    HabitLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(HabitLog.log_date.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_user_and_date_range(
        self, user_id: str, since: date, until: date
    ) -> list[HabitLog]:
        return list(
            self.session.exec(
                select(HabitLog).where(
                    HabitLog.user_id == user_id,
                    HabitLog.log_date >= since,
                    HabitLog.log_date <= until,
                    HabitLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
            ).all()
        )

    def find_by_habit_and_date(self, habit_id: str, log_date: date) -> HabitLog | None:
        stmt = select(HabitLog).where(
            HabitLog.habit_id == habit_id,
            HabitLog.log_date == log_date,
            HabitLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        return self.session.exec(stmt).first()

    def find_all_by_user(self, user_id: str) -> list[HabitLog]:
        return list(
            self.session.exec(
                select(HabitLog).where(
                    HabitLog.user_id == user_id,
                    HabitLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(HabitLog.log_date.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )
