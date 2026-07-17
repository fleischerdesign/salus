from datetime import date

from salus.exceptions import NotFoundError
from salus.models.journal import JournalEntry
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.journal import JournalEntryCreate, JournalEntryUpdate


class JournalService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def list_entries(self, user_id: str, page: int = 1, limit: int = 20) -> tuple[list[JournalEntry], int]:
        offset = (page - 1) * limit
        entries = self.uow.journal_entries.find_by_user(user_id, offset, limit)
        total = self.uow.journal_entries.count_by_user(user_id)
        return entries, total

    def get(self, entry_id: str, user_id: str) -> JournalEntry:
        e = self.uow.journal_entries.get_by_id(entry_id)
        if e is None or e.user_id != user_id:
            raise NotFoundError(f"Journal entry {entry_id} not found")
        return e

    def get_by_date(self, user_id: str, entry_date: date) -> JournalEntry | None:
        return self.uow.journal_entries.find_by_user_and_date(user_id, entry_date)

    def create(self, data: JournalEntryCreate, user_id: str) -> JournalEntry:
        entry = JournalEntry(
            user_id=user_id,
            entry_date=data.entry_date or date.today(),
            title=data.title,
            content=data.content,
            mood_score=data.mood_score,
            is_private=data.is_private,
        )
        return self.uow.journal_entries.create(entry)

    def update(self, entry_id: str, user_id: str, data: JournalEntryUpdate) -> JournalEntry:
        e = self.get(entry_id, user_id)
        if data.title is not None:
            e.title = data.title
        if data.content is not None:
            e.content = data.content
        if data.mood_score is not None:
            e.mood_score = data.mood_score
        if data.is_private is not None:
            e.is_private = data.is_private
        return self.uow.journal_entries.update(e)

    def delete(self, entry_id: str, user_id: str) -> None:
        e = self.get(entry_id, user_id)
        self.uow.journal_entries.delete(e)

    def search(self, user_id: str, query: str, page: int = 1, limit: int = 20) -> list[JournalEntry]:
        offset = (page - 1) * limit
        return self.uow.journal_entries.search(user_id, query, offset, limit)
