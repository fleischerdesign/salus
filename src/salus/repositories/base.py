from datetime import datetime, timezone
from typing import Generic, TypeVar

from sqlmodel import Session

T = TypeVar("T")


class Repository(Generic[T]):
    model: type[T]

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: str) -> T | None:
        obj = self.session.get(self.model, id)
        if obj and hasattr(obj, 'deleted_at') and obj.deleted_at is not None:  # pyright: ignore[reportAttributeAccessIssue]
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
            obj.deleted_at = datetime.now(timezone.utc)  # pyright: ignore[reportAttributeAccessIssue]
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
