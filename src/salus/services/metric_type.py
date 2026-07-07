from salus.exceptions import ConflictError, NotFoundError
from salus.models import MetricType
from salus.repositories.protocols import IMetricTypeRepository
from salus.schemas import MetricTypeCreate


class MetricTypeService:
    def __init__(self, repo: IMetricTypeRepository) -> None:
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
        existing = self.repo.find_by_name_and_user(data.name, user_id)
        if existing is not None:
            raise ConflictError(f"MetricType '{data.name}' already exists")
        metric_type = MetricType(**data.model_dump(), user_id=user_id)
        return self.repo.create(metric_type)

    def update(
        self, metric_type_id: int, user_id: int, data: MetricTypeCreate
    ) -> MetricType:
        metric_type = self.get(metric_type_id, user_id)
        existing = self.repo.find_by_name_and_user(data.name, user_id)
        if existing is not None and existing.id != metric_type_id:
            raise ConflictError(f"MetricType '{data.name}' already exists")
        for field, value in data.model_dump().items():
            setattr(metric_type, field, value)
        return self.repo.update(metric_type)

    def delete(self, metric_type_id: int, user_id: int) -> None:
        metric_type = self.get(metric_type_id, user_id)
        if metric_type.is_system:
            raise ConflictError("Cannot delete system metric types")
        self.repo.delete(metric_type)

    def reorder(self, user_id: int, ordered_ids: list[int]) -> None:
        self.repo.reorder(user_id, ordered_ids)
