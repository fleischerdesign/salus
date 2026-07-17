from datetime import date

from sqlmodel import select

from salus.models.mood import MoodEntry, MoodTag
from salus.repositories.base import Repository


class MoodTagRepository(Repository[MoodTag]):
    model = MoodTag

    def find_all_tags(self) -> list[MoodTag]:
        return list(self.session.exec(select(MoodTag)).all())


class MoodEntryRepository(Repository[MoodEntry]):
    model = MoodEntry

    def find_by_user(self, user_id: str) -> list[MoodEntry]:
        return list(
            self.session.exec(
                select(MoodEntry).where(
                    MoodEntry.user_id == user_id,
                    MoodEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(MoodEntry.entry_date.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_user_range(
        self, user_id: str, since: date, until: date
    ) -> list[MoodEntry]:
        return list(
            self.session.exec(
                select(MoodEntry).where(
                    MoodEntry.user_id == user_id,
                    MoodEntry.entry_date >= since,
                    MoodEntry.entry_date <= until,
                    MoodEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(MoodEntry.entry_date.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_user_and_date(
        self, user_id: str, entry_date: date
    ) -> MoodEntry | None:
        stmt = select(MoodEntry).where(
            MoodEntry.user_id == user_id,
            MoodEntry.entry_date == entry_date,
            MoodEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        return self.session.exec(stmt).first()
