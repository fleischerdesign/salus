from sqlmodel import select

from salus.models.metric_definition import MetricDefinition
from salus.repositories.base import Repository
from salus.repositories.protocols import IMetricDefinitionRepository


class MetricDefinitionRepository(Repository[MetricDefinition], IMetricDefinitionRepository):
    model = MetricDefinition

    def find_all(self, user_id: str | None = None) -> list[MetricDefinition]:
        return list(self.session.exec(
            select(MetricDefinition).order_by(MetricDefinition.sort_order)  # pyright: ignore[reportArgumentType]
        ).all())

    def find_by_code(self, code: str) -> MetricDefinition | None:
        return self.session.get(MetricDefinition, code)

    def find_by_source_data_type(self, source_data_type: str) -> MetricDefinition | None:
        return self.session.exec(
            select(MetricDefinition).where(MetricDefinition.source_data_type == source_data_type)
        ).first()

    def find_by_group(self, group_key: str) -> list[MetricDefinition]:
        return list(self.session.exec(
            select(MetricDefinition)
            .where(MetricDefinition.group_key == group_key)
            .order_by(MetricDefinition.sort_order)  # pyright: ignore[reportArgumentType]
        ).all())
