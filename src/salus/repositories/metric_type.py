from sqlmodel import select

from salus.models import MetricType
from salus.repositories.base import Repository


class MetricTypeRepository(Repository[MetricType]):
    model = MetricType

    def find_all(self, user_id: int | None = None) -> list[MetricType]:
        stmt = select(MetricType)
        if user_id is not None:
            stmt = stmt.where(MetricType.user_id == user_id)
        return list(self.session.exec(stmt).all())

    def find_by_name(self, name: str) -> MetricType | None:
        stmt = select(MetricType).where(MetricType.name == name).limit(1)
        return self.session.exec(stmt).first()

    def find_by_name_and_user(self, name: str, user_id: int) -> MetricType | None:
        stmt = select(MetricType).where(
            MetricType.name == name, MetricType.user_id == user_id
        )
        return self.session.exec(stmt).first()
