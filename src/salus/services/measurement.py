import logging
import math
from datetime import datetime, timezone
from typing import Any

from salus.exceptions import NotFoundError
from salus.models.measurement import Measurement
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.measurement import MeasurementCreate
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

    def find_by_metric_type_paginated(
        self,
        metric_code: str,
        user_id: str,
        page: int = 1,
        per_page: int = 25,
    ) -> tuple[list[Measurement], int, int]:
        offset = (page - 1) * per_page
        entries, total = self.uow.measurements.find_by_metric_type_paginated(
            metric_code, user_id, offset, per_page
        )
        total_pages = max(1, math.ceil(total / per_page)) if total > 0 else 1
        return entries, total, total_pages

    def get_metric_overview(
        self, user_id: str, metric_ids: list[str]
    ) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for mid in metric_ids:
            latest = self.uow.measurements.get_latest_by_metric_type(mid, user_id)
            count = self.uow.measurements.count_by_metric_type(mid, user_id)
            result[mid] = {
                "latest_value": latest.display_value if latest else None,
                "latest_date": latest.start_time.strftime("%Y-%m-%d %H:%M")
                if latest
                else None,
                "entry_count": count,
            }
        return result

    def find_recent(self, user_id: str, limit: int = 20) -> list[Measurement]:
        return self.uow.measurements.find_recent_entries(user_id, limit)

    def create(
        self, data: MeasurementCreate, metric_code: str, user_id: str
    ) -> Measurement:
        obj = Measurement(
            user_id=user_id,
            metric_code=metric_code,
            data_type="",
            source="manual",
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
