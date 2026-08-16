import logging
from typing import TYPE_CHECKING

from salus.models.measurement import Measurement
from salus.models.user_source_preference import UserSourcePreference
from salus.models.user_source_status import UserSourceStatus
from salus.schemas.user_source_preference import (
    BulkSourcePriorityUpdate,
    MetricSourcePriorityItem,
)
from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork

logger = logging.getLogger("salus.service.source_resolution")


class SourceResolutionService:
    def __init__(self, uow: "IUnitOfWork") -> None:
        self.uow = uow

    def get_user_preferences(self, user_id: str) -> dict[str, list[UserSourcePreference]]:
        prefs = self.uow.user_source_preferences.find_by_user(user_id)
        grouped: dict[str, list[UserSourcePreference]] = {}
        for p in prefs:
            grouped.setdefault(p.metric_code, []).append(p)
        return grouped

    def get_metric_preferences(self, user_id: str, metric_code: str) -> list[UserSourcePreference]:
        return self.uow.user_source_preferences.find_by_user_and_metric(user_id, metric_code)

    def set_metric_preferences(
        self, user_id: str, metric_code: str, items: list[MetricSourcePriorityItem]
    ) -> list[UserSourcePreference]:
        existing = self.uow.user_source_preferences.find_by_user_and_metric(user_id, metric_code)
        existing_map = {p.source: p for p in existing}
        result: list[UserSourcePreference] = []

        for item in items:
            pref = existing_map.get(item.source)
            if pref:
                pref.priority_rank = item.priority_rank
                pref.is_enabled = item.is_enabled
                self.uow.user_source_preferences.update(pref)
                result.append(pref)
            else:
                new_pref = UserSourcePreference(
                    id=uuid7_str(),
                    user_id=user_id,
                    metric_code=metric_code,
                    source=item.source,
                    priority_rank=item.priority_rank,
                    is_enabled=item.is_enabled,
                )
                self.uow.user_source_preferences.create(new_pref)
                result.append(new_pref)

        return result

    def bulk_set_preferences(
        self, user_id: str, updates: list[BulkSourcePriorityUpdate]
    ) -> dict[str, list[UserSourcePreference]]:
        res: dict[str, list[UserSourcePreference]] = {}
        for u in updates:
            res[u.metric_code] = self.set_metric_preferences(user_id, u.metric_code, u.priorities)
        return res

    def get_source_statuses(self, user_id: str) -> list[UserSourceStatus]:
        return self.uow.user_source_statuses.find_by_user(user_id)

    def set_source_status(self, user_id: str, source: str, connected: bool) -> UserSourceStatus:
        existing = self.uow.user_source_statuses.find_by_user_source(user_id, source)
        if existing:
            existing.connected = connected
            return self.uow.user_source_statuses.update(existing)
        new_status = UserSourceStatus(
            id=uuid7_str(),
            user_id=user_id,
            source=source,
            connected=connected,
        )
        return self.uow.user_source_statuses.create(new_status)

    def resolve_measurements(self, user_id: str, records: list[Measurement]) -> list[Measurement]:
        if not records:
            return records

        user_prefs = self.get_user_preferences(user_id)
        if not user_prefs:
            return records

        resolved: list[Measurement] = []
        for rec in records:
            metric_code = rec.metric_code or rec.source_data_type
            prefs = user_prefs.get(metric_code, [])
            pref_map = {p.source: p for p in prefs}

            source_pref = pref_map.get(rec.source)
            if source_pref and not source_pref.is_enabled:
                logger.info(
                    "Dropping record | source=%s | metric=%s (Disabled by UserSourcePreference)",
                    rec.source,
                    metric_code,
                )
                continue

            resolved.append(rec)

        return resolved
