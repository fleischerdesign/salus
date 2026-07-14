from sqlmodel import select
from typing import Optional

from salus.models.asymmetric_share import ShareRecipient, AsymmetricShare
from salus.repositories.base import Repository
from salus.repositories.protocols import IShareRecipientRepository, IAsymmetricShareRepository


class ShareRecipientRepository(Repository[ShareRecipient], IShareRecipientRepository):
    model = ShareRecipient

    def find_by_user(self, user_id: str) -> list[ShareRecipient]:
        return list(
            self.session.exec(
                select(ShareRecipient).where(ShareRecipient.user_id == user_id)
            ).all()
        )


class AsymmetricShareRepository(Repository[AsymmetricShare], IAsymmetricShareRepository):
    model = AsymmetricShare

    def find_by_user(self, user_id: str) -> list[AsymmetricShare]:
        return list(
            self.session.exec(
                select(AsymmetricShare).where(AsymmetricShare.user_id == user_id)
            ).all()
        )

    def get_by_id_secure(self, share_id: str) -> Optional[AsymmetricShare]:
        share = self.session.get(AsymmetricShare, share_id)
        if share and share.deleted_at is not None:
            return None
        return share
