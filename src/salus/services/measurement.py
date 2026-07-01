from datetime import datetime, timezone

from salus.exceptions import NotFoundError
from salus.models.measurement import Measurement
from salus.repositories.protocols import IMeasurementRepository
from salus.schemas.measurement import MeasurementCreate


class MeasurementService:
    def __init__(self, repo: IMeasurementRepository) -> None:
        self.repo = repo

    def get(self, measurement_id: int, user_id: int) -> Measurement:
        obj = self.repo.get_by_id(measurement_id)
        if obj is None:
            raise NotFoundError(f"Measurement {measurement_id} not found")
        if obj.user_id != user_id:
            raise NotFoundError(f"Measurement {measurement_id} not found")
        return obj

    def find_by_metric_type(
        self, metric_type_id: int, user_id: int
    ) -> list[Measurement]:
        return self.repo.find_by_metric_type(metric_type_id, user_id)

    def find_recent(self, user_id: int, limit: int = 20) -> list[Measurement]:
        return self.repo.find_recent_entries(user_id, limit)

    def create(
        self, data: MeasurementCreate, metric_type_id: int, user_id: int
    ) -> Measurement:
        obj = Measurement(
            user_id=user_id,
            metric_type_id=metric_type_id,
            data_type="",
            source="manual",
            value_text=data.value,
            start_time=data.timestamp or datetime.now(timezone.utc),
            notes=data.notes,
        )
        return self.repo.create(obj)

    def update(
        self, measurement_id: int, user_id: int, data: MeasurementCreate
    ) -> Measurement:
        obj = self.get(measurement_id, user_id)
        obj.value_text = data.value
        if data.timestamp is not None:
            obj.start_time = data.timestamp
        obj.notes = data.notes
        return self.repo.update(obj)

    def delete(self, measurement_id: int, user_id: int) -> None:
        obj = self.get(measurement_id, user_id)
        self.repo.delete(obj)
