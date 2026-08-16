import logging
from datetime import datetime, timezone

from salus.exceptions import NotFoundError
from salus.models.measurement import Measurement
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.measurement import HealthMeasurementIn, MeasurementCreate
from salus.services.constants import SOURCE_MANUAL, SOURCE_HEALTH_CONNECT
from salus.services.plugin.hooks import HookRegistry

logger = logging.getLogger("salus.services.measurement")


class MeasurementService:
    def __init__(
        self, uow: IUnitOfWork, registry: HookRegistry | None = None
    ) -> None:
        self.uow = uow
        self._registry = registry

    def get(self, measurement_id: str, user_id: str) -> Measurement:
        obj = self.uow.measurements.get_by_id(measurement_id)
        if obj is None:
            raise NotFoundError(f"Measurement {measurement_id} not found")
        if obj.user_id != user_id:
            raise NotFoundError(f"Measurement {measurement_id} not found")
        return obj

    def find_by_metric_type(
        self, metric_code: str, user_id: str
    ) -> list[Measurement]:
        return self.uow.measurements.find_by_metric_type(metric_code, user_id)

    def find_recent(self, user_id: str, limit: int = 20) -> list[Measurement]:
        return self.uow.measurements.find_recent_entries(user_id, limit)

    def create(
        self, data: MeasurementCreate, metric_code: str, user_id: str
    ) -> Measurement:
        obj = Measurement(
            user_id=user_id,
            metric_code=metric_code,
            source_data_type="",
            source=SOURCE_MANUAL,
            value_text=data.value,
            start_time=data.timestamp or datetime.now(timezone.utc),
            notes=data.notes,
        )
        res = self.uow.measurements.create(obj)
        if self._registry:
            for sub in self._registry.event_subscribers:
                try:
                    sub.on_measurement_created(res)
                except Exception as e:
                    logger.error(
                        f"Error notifying event subscriber on measurement creation: {e}"
                    )
        return res

    def update(
        self, measurement_id: str, user_id: str, data: MeasurementCreate
    ) -> Measurement:
        obj = self.get(measurement_id, user_id)
        obj.value_text = data.value
        if data.timestamp is not None:
            obj.start_time = data.timestamp
        obj.notes = data.notes
        return self.uow.measurements.update(obj)

    def delete(self, measurement_id: str, user_id: str) -> None:
        obj = self.get(measurement_id, user_id)
        self.uow.measurements.delete(obj)

    def bulk_upsert_health(
        self, measurements: list[HealthMeasurementIn], user_id: str
    ) -> tuple[int, int]:
        """Bulk replicate device health measurements.

        Idempotent insert-or-update keyed by ``(external_id, source)`` so a re-seed
        after an app-data wipe never duplicates rows. Returns ``(inserted, duplicates)``.
        """
        records = [
            Measurement(
                id=m.id,
                user_id=user_id,
                metric_code=m.metric_code,
                source_data_type=m.source_data_type,
                source=SOURCE_HEALTH_CONNECT,
                value_numeric=m.value_numeric,
                value_text=m.value_text,
                value_json=m.value_json,
                start_time=m.start_time,
                end_time=m.end_time,
                external_id=m.external_id,
                created_at=m.created_at or m.start_time,
                updated_at=m.updated_at,
            )
            for m in measurements
        ]
        return self.uow.measurements.upsert_all(records)[:2]
