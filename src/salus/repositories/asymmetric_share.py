from sqlmodel import select
from typing import Optional

from salus.models.asymmetric_share import ShareRecipient, AsymmetricShare
from salus.repositories.base import Repository


class ShareRecipientRepository(Repository[ShareRecipient]):
    model = ShareRecipient

    def find_by_user(self, user_id: int) -> list[ShareRecipient]:
        return list(
            self.session.exec(
                select(ShareRecipient).where(ShareRecipient.user_id == user_id)
            ).all()
        )


class AsymmetricShareRepository(Repository[AsymmetricShare]):
    model = AsymmetricShare

    def find_by_user(self, user_id: int) -> list[AsymmetricShare]:
        return list(
            self.session.exec(
                select(AsymmetricShare).where(AsymmetricShare.user_id == user_id)
            ).all()
        )

    def get_by_id_secure(self, share_id: int) -> Optional[AsymmetricShare]:
        return self.session.get(AsymmetricShare, share_id)
