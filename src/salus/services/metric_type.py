from salus.exceptions import NotFoundError
from salus.models import MetricType
from salus.repositories.metric_type import MetricTypeRepository
from salus.schemas import MetricTypeCreate


class MetricTypeService:
    def __init__(self, repo: MetricTypeRepository) -> None:
        self.repo = repo

    def get(self, metric_type_id: int, user_id: int) -> MetricType:
        metric_type = self.repo.get_by_id(metric_type_id)
        if metric_type is None:
            raise NotFoundError(f"MetricType {metric_type_id} not found")
        if metric_type.user_id != user_id:
            raise NotFoundError(f"MetricType {metric_type_id} not found")
        return metric_type

    def find_all(self, user_id: int) -> list[MetricType]:
        return self.repo.find_all(user_id)

    def create(self, data: MetricTypeCreate, user_id: int) -> MetricType:
        metric_type = MetricType(**data.model_dump(), user_id=user_id)
        return self.repo.create(metric_type)

    def update(self, metric_type_id: int, user_id: int, data: MetricTypeCreate) -> MetricType:
        metric_type = self.get(metric_type_id, user_id)
        for field, value in data.model_dump().items():
            setattr(metric_type, field, value)
        return self.repo.update(metric_type)

    def delete(self, metric_type_id: int, user_id: int) -> None:
        metric_type = self.get(metric_type_id, user_id)
        self.repo.delete(metric_type)
