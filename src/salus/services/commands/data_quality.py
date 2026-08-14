from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from salus.services._helpers import uid
from salus.services.command_registry import CommandResult, register
from salus.services.data_quality import DataQualityService

if TYPE_CHECKING:
    from salus.models.user import User
    from salus.repositories.unit_of_work import IUnitOfWork


@register("data_quality_recheck")
class DataQualityRecheckHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        user_id = uid(user)
        counts = DataQualityService(uow).run_checks(user_id)
        uow.commit()
        return CommandResult(status="ok", extra=counts)


@register("data_quality_acknowledge")
class DataQualityAcknowledgeHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        flag_id = payload.get("flag_id")
        if not flag_id:
            return CommandResult(status="error", message="flag_id is required")

        flag = uow.data_quality_flags.get_by_id(flag_id)
        if not flag or flag.user_id != uid(user):
            return CommandResult(status="not_found", message="Flag not found")

        flag.resolved_at = datetime.now(timezone.utc)
        uow.data_quality_flags.update(flag)
        uow.commit()
        return CommandResult(status="updated", id=flag_id)
