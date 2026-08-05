from datetime import date

from sqlmodel import col, select

from salus.models.journal import JournalEntry
from salus.repositories.base import Repository


class JournalEntryRepository(Repository[JournalEntry]):
    model = JournalEntry

    def find_by_user(self, user_id: str, offset: int = 0, limit: int = 20) -> list[JournalEntry]:
        return list(
            self.session.exec(
                select(JournalEntry)
                .where(
                    JournalEntry.user_id == user_id,
                    JournalEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
                .order_by(col(JournalEntry.entry_date).desc())
                .offset(offset)
                .limit(limit)
            ).all()
        )

    def count_by_user(self, user_id: str) -> int:
        from sqlalchemy import func
        stmt = (
            select(func.count())
            .select_from(JournalEntry)
            .where(
                JournalEntry.user_id == user_id,
                JournalEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
        )
        return self.session.exec(stmt).one()

    def find_by_user_range(
        self, user_id: str, since: date, until: date
    ) -> list[JournalEntry]:
        return list(
            self.session.exec(
                select(JournalEntry)
                .where(
                    JournalEntry.user_id == user_id,
                    col(JournalEntry.entry_date) >= since,
                    col(JournalEntry.entry_date) <= until,
                    JournalEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
                .order_by(col(JournalEntry.entry_date).desc())
            ).all()
        )

    def find_by_user_and_date(
        self, user_id: str, entry_date: date
    ) -> JournalEntry | None:
        stmt = select(JournalEntry).where(
            JournalEntry.user_id == user_id,
            col(JournalEntry.entry_date) == entry_date,
            JournalEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        return self.session.exec(stmt).first()

    def search(self, user_id: str, query: str, offset: int = 0, limit: int = 20) -> list[JournalEntry]:
        return list(
            self.session.exec(
                select(JournalEntry)
                .where(
                    JournalEntry.user_id == user_id,
                    col(JournalEntry.content).contains(query),
                    JournalEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
                .order_by(col(JournalEntry.entry_date).desc())
                .offset(offset)
                .limit(limit)
            ).all()
        )
