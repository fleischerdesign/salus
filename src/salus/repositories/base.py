from typing import Generic, TypeVar

from sqlmodel import Session

T = TypeVar("T")


class Repository(Generic[T]):
    model: type[T]

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, id: int) -> T | None:
        return self.session.get(self.model, id)

    def create(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)
        self.session.commit()
