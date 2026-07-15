from __future__ import annotations

from typing import Any, TYPE_CHECKING

from salus.models.user import User
from salus.services.command_registry import CommandResult, register

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork


@register("toggle_admin")
class ToggleAdminHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        if not user.is_admin:
            return CommandResult(status="forbidden", message="Admin access required")
        target_id = payload.get("user_id")
        if not target_id:
            return CommandResult(status="error", message="user_id is required")
        target = uow.users.get_by_id(target_id)  # pyright: ignore[reportArgumentType]
        if not target:
            return CommandResult(status="not_found", message=f"User {target_id} not found")
        target.is_admin = not target.is_admin
        uow.users.update(target)
        uow.commit()
        uow.session.refresh(target)
        record: dict[str, Any] = {"id": target.id, "username": target.username,
            "is_admin": target.is_admin, "is_active": target.is_active}
        return CommandResult(status="updated", record=record, id=target_id)


@register("toggle_active")
class ToggleActiveHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        if not user.is_admin:
            return CommandResult(status="forbidden", message="Admin access required")
        target_id = payload.get("user_id")
        if not target_id:
            return CommandResult(status="error", message="user_id is required")
        target = uow.users.get_by_id(target_id)  # pyright: ignore[reportArgumentType]
        if not target:
            return CommandResult(status="not_found", message=f"User {target_id} not found")
        target.is_active = not target.is_active
        uow.users.update(target)
        uow.commit()
        uow.session.refresh(target)
        record: dict[str, Any] = {"id": target.id, "username": target.username,
            "is_admin": target.is_admin, "is_active": target.is_active}
        return CommandResult(status="updated", record=record, id=target_id)


@register("delete_user")
class DeleteUserHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        if not user.is_admin:
            return CommandResult(status="forbidden", message="Admin access required")
        target_id = payload.get("user_id")
        if not target_id:
            return CommandResult(status="error", message="user_id is required")
        if target_id == user.id:  # pyright: ignore[reportArgumentType]
            return CommandResult(status="error", message="Cannot delete your own account")

        target = uow.users.get_by_id(target_id)  # pyright: ignore[reportArgumentType]
        if not target:
            return CommandResult(status="not_found", message=f"User {target_id} not found")

        for token in uow.api_tokens.find_all_by_user(target_id):  # pyright: ignore[reportArgumentType]
            uow.api_tokens.delete(token)
        for widget in uow.dashboard_widgets.find_by_user(target_id):  # pyright: ignore[reportArgumentType]
            uow.dashboard_widgets.delete(widget)
        uow.users.delete(target)
        uow.commit()
        return CommandResult(status="deleted", id=target_id)


@register("admin_revoke_token")
class AdminRevokeTokenHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        if not user.is_admin:
            return CommandResult(status="forbidden", message="Admin access required")
        token_id = payload.get("id")
        if not token_id:
            return CommandResult(status="error", message="id is required")
        token = uow.api_tokens.get_by_id(token_id)  # pyright: ignore[reportArgumentType]
        if not token:
            return CommandResult(status="not_found", id=token_id)
        token.is_active = False
        uow.api_tokens.update(token)
        uow.commit()
        return CommandResult(status="updated", id=token_id)


@register("set_config")
class SetConfigHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        if not user.is_admin:
            return CommandResult(status="forbidden", message="Admin access required")
        key = payload.get("key")
        value = payload.get("value")
        if not key:
            return CommandResult(status="error", message="key is required")
        uow.system_configs.upsert(key, value or "")
        uow.commit()
        record: dict[str, Any] = {"key": key, "value": value}
        return CommandResult(status="updated", record=record)