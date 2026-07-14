from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, TYPE_CHECKING

from salus.models.asymmetric_share import AsymmetricShare, ShareRecipient
from salus.services.command_registry import CommandResult, register

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User


@register("create_share_recipient")
class CreateShareRecipientHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        recipient = ShareRecipient(
            id=payload.get("id"),
            user_id=user.id,  # pyright: ignore[reportArgumentType]
            name=payload["name"],
            public_key=payload["public_key"],
        )
        uow.share_recipients.add(recipient)
        uow.commit()
        uow.session.refresh(recipient)
        record: dict[str, Any] = {"id": recipient.id, "user_id": recipient.user_id,
            "name": recipient.name, "public_key": recipient.public_key}
        return CommandResult(status="created", record=record, id=recipient.id)  # pyright: ignore[reportAttributeAccessIssue]


@register("delete_share_recipient")
class DeleteShareRecipientHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        recipient_id = payload.get("id")
        if not recipient_id:
            return CommandResult(status="error", message="id is required")
        recipient = uow.share_recipients.get_by_id(recipient_id)  # pyright: ignore[reportArgumentType]
        if not recipient or recipient.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="not_found", id=recipient_id)
        uow.share_recipients.delete(recipient)
        uow.commit()
        return CommandResult(status="deleted", id=recipient_id)


@register("create_asymmetric_share")
class CreateAsymmetricShareHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        recipient_id = payload.get("recipient_id") or ""
        recipient = uow.share_recipients.get_by_id(recipient_id)  # pyright: ignore[reportArgumentType]
        if not recipient or recipient.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="error", message="Recipient not found")

        expires_at = None
        if payload.get("expires_in_hours") is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=payload["expires_in_hours"])

        share = AsymmetricShare(
            id=payload.get("id"),
            user_id=user.id,  # pyright: ignore[reportArgumentType]
            recipient_id=recipient_id,
            encrypted_data=payload["encrypted_data"],
            encrypted_key=payload["encrypted_key"],
            expires_at=expires_at,
        )
        uow.asymmetric_shares.add(share)
        uow.commit()
        uow.session.refresh(share)
        record: dict[str, Any] = {"id": share.id, "user_id": share.user_id,
            "recipient_id": share.recipient_id, "encrypted_data": share.encrypted_data,
            "encrypted_key": share.encrypted_key, "expires_at": share.expires_at}
        return CommandResult(status="created", record=record, id=share.id)  # pyright: ignore[reportAttributeAccessIssue]


@register("delete_asymmetric_share")
class DeleteAsymmetricShareHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        share_id = payload.get("id")
        if not share_id:
            return CommandResult(status="error", message="id is required")
        share = uow.asymmetric_shares.get_by_id(share_id)  # pyright: ignore[reportArgumentType]
        if not share or share.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="not_found", id=share_id)
        uow.asymmetric_shares.delete(share)
        uow.commit()
        return CommandResult(status="deleted", id=share_id)