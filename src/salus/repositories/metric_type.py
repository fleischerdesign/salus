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
