from sqlmodel import select

from salus.models.user_identity import UserIdentity
from salus.repositories.base import Repository


class UserIdentityRepository(Repository[UserIdentity]):
    model = UserIdentity

    def get_by_provider_user_id(self, provider: str, provider_user_id: str) -> UserIdentity | None:
        return self.session.exec(
            select(UserIdentity).where(
                UserIdentity.provider == provider,
                UserIdentity.provider_user_id == provider_user_id,
            )
        ).first()

    def list_by_user(self, user_id: int) -> list[UserIdentity]:
        return list(
            self.session.exec(
                select(UserIdentity).where(UserIdentity.user_id == user_id)
            ).all()
        )
