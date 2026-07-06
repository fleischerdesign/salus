import logging
import math
from datetime import datetime, timezone

from salus.exceptions import NotFoundError
from salus.models.measurement import Measurement
from salus.repositories.protocols import IMeasurementRepository
from salus.schemas.measurement import MeasurementCreate
from salus.services.plugin.hooks import HookRegistry

logger = logging.getLogger("salus.services.measurement")


class MeasurementService:
    def __init__(self, repo: IMeasurementRepository, registry: HookRegistry | None = None) -> None:
        self.repo = repo
        self._registry = registry

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

    def find_by_metric_type_paginated(
        self, metric_type_id: int, user_id: int, page: int = 1, per_page: int = 25,
    ) -> tuple[list[Measurement], int, int]:
        offset = (page - 1) * per_page
        entries, total = self.repo.find_by_metric_type_paginated(metric_type_id, user_id, offset, per_page)
        total_pages = max(1, math.ceil(total / per_page)) if total > 0 else 1
        return entries, total, total_pages

    def get_metric_overview(self, user_id: int, metric_ids: list[int]) -> dict[int, dict]:
        result: dict[int, dict] = {}
        for mid in metric_ids:
            latest = self.repo.get_latest_by_metric_type(mid, user_id)
            count = self.repo.count_by_metric_type(mid, user_id)
            result[mid] = {
                "latest_value": latest.display_value if latest else None,
                "latest_date": latest.start_time.strftime("%Y-%m-%d %H:%M") if latest else None,
                "entry_count": count,
            }
        return result

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
        res = self.repo.create(obj)
        if self._registry:
            for sub in self._registry.event_subscribers:
                try:
                    sub.on_measurement_created(res)
                except Exception as e:
                    logger.error(f"Error notifying event subscriber on measurement creation: {e}")
        return res

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
