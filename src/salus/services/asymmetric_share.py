from datetime import datetime, timedelta, timezone

from salus.exceptions import NotFoundError
from salus.models.asymmetric_share import ShareRecipient, AsymmetricShare
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.asymmetric_share import AsymmetricShareCreate, ShareRecipientCreate


class AsymmetricShareService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def create_recipient(self, user_id: int, data: ShareRecipientCreate) -> ShareRecipient:
        with self.uow:
            recipient = ShareRecipient(
                user_id=user_id,
                name=data.name,
                public_key=data.public_key,
            )
            self.uow.share_recipients.add(recipient)
            self.uow.commit()
            return recipient

    def list_recipients(self, user_id: int) -> list[ShareRecipient]:
        with self.uow:
            return self.uow.share_recipients.find_by_user(user_id)

    def delete_recipient(self, user_id: int, recipient_id: int) -> None:
        with self.uow:
            recipient = self.uow.share_recipients.get_by_id(recipient_id)
            if not recipient or recipient.user_id != user_id:
                raise NotFoundError("Recipient not found.")
            self.uow.share_recipients.delete(recipient)
            self.uow.commit()

    def create_share(self, user_id: int, data: AsymmetricShareCreate) -> AsymmetricShare:
        with self.uow:
            recipient = self.uow.share_recipients.get_by_id(data.recipient_id)
            if not recipient or recipient.user_id != user_id:
                raise NotFoundError("Recipient not found.")

            expires_at = None
            if data.expires_in_hours is not None:
                expires_at = datetime.now(timezone.utc) + timedelta(hours=data.expires_in_hours)

            share = AsymmetricShare(
                user_id=user_id,
                recipient_id=data.recipient_id,
                encrypted_data=data.encrypted_data,
                encrypted_key=data.encrypted_key,
                expires_at=expires_at,
            )
            self.uow.asymmetric_shares.add(share)
            self.uow.commit()
            return share

    def get_share_secure(self, share_id: int) -> AsymmetricShare:
        """
        Public endpoint to fetch a share. Since it is fully client-side encrypted,
        we do not authenticate the request, but we enforce expiration dates.
        """
        with self.uow:
            share = self.uow.asymmetric_shares.get_by_id_secure(share_id)
            if not share:
                raise NotFoundError("Share link not found or expired.")

            # Enforce expiration
            if share.expires_at is not None:
                if datetime.now(timezone.utc) > share.expires_at.replace(tzinfo=timezone.utc):
                    # Auto clean up expired share
                    self.uow.asymmetric_shares.delete(share)
                    self.uow.commit()
                    raise NotFoundError("Share link not found or expired.")

            return share

    def list_shares(self, user_id: int) -> list[AsymmetricShare]:
        with self.uow:
            return self.uow.asymmetric_shares.find_by_user(user_id)

    def delete_share(self, user_id: int, share_id: int) -> None:
        with self.uow:
            share = self.uow.asymmetric_shares.get_by_id_secure(share_id)
            if not share or share.user_id != user_id:
                raise NotFoundError("Share not found.")
            self.uow.asymmetric_shares.delete(share)
            self.uow.commit()
