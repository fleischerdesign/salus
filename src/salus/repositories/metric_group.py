from sqlmodel import select

from salus.models.metric_definition import MetricGroup
from salus.repositories.base import Repository
from salus.repositories.protocols import IMetricGroupRepository


class MetricGroupRepository(Repository[MetricGroup], IMetricGroupRepository):
    model = MetricGroup

    def find_all(self, user_id: str | None = None) -> list[MetricGroup]:
        return list(self.session.exec(
            select(MetricGroup)
        ).all())

    def find_by_key(self, key: str) -> MetricGroup | None:
        return self.session.get(MetricGroup, key)
