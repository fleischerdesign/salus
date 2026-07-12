from datetime import datetime, timezone
from typing import Generic, TypeVar

from sqlmodel import Session, select

T = TypeVar("T")


class Repository(Generic[T]):
    model: type[T]

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> T | None:
        obj = self.session.get(self.model, id)
        if obj and hasattr(obj, 'deleted_at') and obj.deleted_at is not None:
            return None
        return obj

    def create(self, obj: T, auto_commit: bool = True) -> T:
        self.session.add(obj)
        if auto_commit:
            self.session.commit()
            self.session.refresh(obj)
        return obj

    def update(self, obj: T, auto_commit: bool = True) -> T:
        self.session.add(obj)
        if auto_commit:
            self.session.commit()
            self.session.refresh(obj)
        return obj

    def delete(self, obj: T, auto_commit: bool = True) -> None:
        if hasattr(obj, 'deleted_at'):
            obj.deleted_at = datetime.now(timezone.utc)
            self.session.add(obj)
        else:
            self.session.delete(obj)
        if auto_commit:
            self.session.commit()

    def add(self, obj: T) -> None:
        """Add an entity to the session without committing immediately."""
        self.session.add(obj)

    def add_all(self, objs: list[T]) -> None:
        """Add multiple entities to the session without committing immediately."""
        for obj in objs:
            self.session.add(obj)

    def commit(self) -> None:
        """Commit the current transaction."""
        self.session.commit()

    # ── Sync helpers ──

    def find_updated_since(self, since: datetime) -> list[T]:
        """Return all non-deleted records updated since the given timestamp."""
        stmt = select(self.model).where(
            getattr(self.model, 'updated_at') >= since,
            getattr(self.model, 'deleted_at').is_(None),
        )
        return list(self.session.exec(stmt).all())

    def find_deleted_since(self, since: datetime) -> list[int]:
        """Return IDs of records soft-deleted since the given timestamp."""
        stmt = select(getattr(self.model, 'id')).where(
            getattr(self.model, 'deleted_at') >= since,
        )
        return [row for row in self.session.exec(stmt).all()]
