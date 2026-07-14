from __future__ import annotations

from typing import Any, TYPE_CHECKING

from salus.services.command_registry import CommandResult, register

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User


@register("dismiss_onboarding")
class DismissOnboardingHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        user.onboarding_dismissed = True
        uow.users.update(user)
        uow.commit()
        return CommandResult(status="updated", id=user.id)  # pyright: ignore[reportArgumentType]