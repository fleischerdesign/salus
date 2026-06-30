from sqlmodel import select

from salus.models.user import User
from salus.repositories.base import Repository


class UserRepository(Repository[User]):
    model = User

    def get_by_username(self, username: str) -> User | None:
        return self.session.exec(
            select(User).where(User.username == username)
        ).first()

    def get_by_email(self, email: str) -> User | None:
        return self.session.exec(
            select(User).where(User.email == email)
        ).first()
