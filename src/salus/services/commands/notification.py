from __future__ import annotations

from typing import Any, TYPE_CHECKING

from salus.services.command_registry import CommandResult, register

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User


@register("mark_notification_read")
class MarkNotificationReadHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        notif_id = payload.get("id")
        if not notif_id:
            return CommandResult(status="error", message="id is required")
        notif = uow.notifications.get_by_id(notif_id)  # pyright: ignore[reportArgumentType]
        if not notif or notif.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="not_found", id=notif_id)
        notif.is_read = True
        uow.notifications.update(notif)
        uow.commit()
        return CommandResult(status="updated", id=notif_id)


@register("mark_all_notifications_read")
class MarkAllNotificationsReadHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        uow.notifications.mark_all_read(user.id)  # pyright: ignore[reportArgumentType]
        uow.commit()
        return CommandResult(status="updated")