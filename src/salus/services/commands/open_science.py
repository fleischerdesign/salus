from __future__ import annotations

from typing import Any, TYPE_CHECKING

from salus.services.command_registry import CommandResult, register

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User


@register("synthesize_open_science")
class SynthesizeOpenScienceHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        from salus.services.open_science import OpenScienceService
        from salus.schemas.open_science import OpenScienceSynthesizeRequest

        service = OpenScienceService(uow)
        req = OpenScienceSynthesizeRequest(**payload)
        result = service.synthesize(user.id, req)  # pyright: ignore[reportArgumentType]
        return CommandResult(status="created", record=result)