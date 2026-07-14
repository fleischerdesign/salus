import logging
from typing import Any

from salus.exceptions import ForbiddenError
from salus.repositories.unit_of_work import IUnitOfWork
from salus.models.measurement import Measurement
from salus.models.goal import Goal
from salus.models import MetricType
from salus.models.user import User

logger = logging.getLogger("salus.plugin.context")


class PluginContext:
    def __init__(self, uow: IUnitOfWork, manifest: dict[str, Any]) -> None:
        self._uow = uow
        self.manifest = manifest
        self.plugin_id = manifest.get("id", "unknown_plugin")

    def _check_permission(self, permission: str) -> None:
        permissions = self.manifest.get("permissions", [])
        if permission not in permissions:
            raise ForbiddenError(
                f"Permission denied: Plugin '{self.plugin_id}' lacks required permission '{permission}'"
            )

    def get_measurements(
        self, user_id: str, data_type: str | None = None, limit: int = 100
    ) -> list[Measurement]:
        self._check_permission("measurements:read")
        data_types = [data_type] if data_type else None
        return self._uow.measurements.find_all(
            user_id=user_id, data_types=data_types, limit=limit
        )

    def create_measurement(self, measurement: Measurement) -> Measurement:
        self._check_permission("measurements:write")
        with self._uow:
            res = self._uow.measurements.create(measurement)
        return res

    def get_goals(self, user_id: str) -> list[Goal]:
        self._check_permission("goals:read")
        return self._uow.goals.find_by_user(user_id)

    def get_metric_types(self, user_id: str | None = None) -> list[MetricType]:
        self._check_permission("metric_types:read")
        return self._uow.metric_types.find_all(user_id=user_id)

    def get_user(self, user_id: str) -> User | None:
        self._check_permission("users:read")
        return self._uow.users.get_by_id(user_id)

    def log_info(self, msg: str, *args, **kwargs) -> None:
        logger.info(f"[{self.plugin_id}] " + msg, *args, **kwargs)

    def log_error(self, msg: str, *args, **kwargs) -> None:
        logger.error(f"[{self.plugin_id}] " + msg, *args, **kwargs)
