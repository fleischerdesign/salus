from __future__ import annotations

import secrets
from typing import Any, TYPE_CHECKING

import bcrypt

from salus.models.api_token import ApiToken
from salus.services.command_registry import CommandResult, register
from salus.services.password import hash_password, verify_password

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User

_TOKEN_PREFIX = "sls_"


@register("change_password")
class ChangePasswordHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        current = payload.get("current_password", "")
        new = payload.get("new_password", "")

        if not user.password_hash or not verify_password(current, user.password_hash):
            return CommandResult(status="error", message="Current password is incorrect")

        user.password_hash = hash_password(new)
        uow.users.update(user)
        uow.commit()
        return CommandResult(status="updated", id=user.id)  # pyright: ignore[reportArgumentType]


@register("create_token")
class CreateTokenHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        plaintext = f"{_TOKEN_PREFIX}{secrets.token_urlsafe(24)}"
        token_hash = bcrypt.hashpw(plaintext.encode(), bcrypt.gensalt()).decode()
        prefix = plaintext[:12]

        token = ApiToken(
            id=payload.get("id"),
            token_hash=token_hash,
            token_prefix=prefix,
            label=payload.get("label", ""),
            scopes=payload.get("scopes", ""),
            user_id=user.id,  # pyright: ignore[reportArgumentType]
        )
        uow.api_tokens.add(token)
        uow.commit()
        uow.session.refresh(token)

        record: dict[str, Any] = {
            "id": token.id,
            "token_prefix": token.token_prefix,
            "label": token.label,
            "scopes": token.scopes,
            "user_id": token.user_id,
            "is_active": token.is_active,
            "created_at": token.created_at.isoformat() if hasattr(token.created_at, "isoformat") else token.created_at,
            "plaintext": plaintext,
        }
        return CommandResult(status="created", record=record, id=token.id)


@register("revoke_token")
class RevokeTokenHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        token_id = payload.get("id")
        if not token_id:
            return CommandResult(status="error", message="id is required")
        token = uow.api_tokens.get_by_id(token_id)  # pyright: ignore[reportArgumentType]
        if not token:
            return CommandResult(status="not_found", id=token_id)
        if token.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", id=token_id)
        token.is_active = False
        uow.api_tokens.update(token)
        uow.commit()
        return CommandResult(status="updated", id=token_id)


@register("update_profile")
class UpdateProfileHandler:
    _SAFE_FIELDS = {"theme", "locale", "display_name", "onboarding_dismissed"}

    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        for key, value in payload.items():
            if key in self._SAFE_FIELDS:
                setattr(user, key, value)
        uow.users.update(user)
        uow.commit()
        uow.session.refresh(user)
        record: dict[str, Any] = {
            "id": user.id, "username": user.username,
            "email": user.email, "display_name": user.display_name,
            "theme": user.theme, "locale": user.locale,
            "onboarding_dismissed": user.onboarding_dismissed,
        }
        return CommandResult(status="updated", record=record, id=user.id)  # pyright: ignore[reportArgumentType]