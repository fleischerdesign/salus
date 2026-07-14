from sqlmodel import select

from salus.models import MetricType
from salus.repositories.base import Repository
from salus.repositories.protocols import IMetricTypeRepository


class MetricTypeRepository(Repository[MetricType], IMetricTypeRepository):
    model = MetricType

    def find_all(self, user_id: str | None = None) -> list[MetricType]:
        stmt = select(MetricType).order_by(MetricType.position)  # pyright: ignore[reportArgumentType]
        if user_id is not None:
            stmt = stmt.where(MetricType.user_id == user_id)
        return list(self.session.exec(stmt).all())

    def find_by_name(self, name: str) -> MetricType | None:
        stmt = select(MetricType).where(MetricType.name == name).limit(1)
        return self.session.exec(stmt).first()

    def find_by_name_and_user(self, name: str, user_id: str) -> MetricType | None:
        stmt = select(MetricType).where(
            MetricType.name == name, MetricType.user_id == user_id
        )
        return self.session.exec(stmt).first()

    def reorder(self, user_id: str, ordered_ids: list[str]) -> None:
        for pos, metric_id in enumerate(ordered_ids):
            mt = self.get_by_id(metric_id)
            if mt is not None and mt.user_id == user_id:
                mt.position = pos
                self.session.add(mt)
        self.session.commit()
