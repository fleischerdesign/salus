from sqlmodel import select

from salus.exceptions import NotFoundError
from salus.models.user import User
from salus.repositories.base import Repository
from salus.repositories.protocols import IUserRepository


class UserRepository(Repository[User], IUserRepository):
    model = User

    def get_by_username(self, username: str) -> User | None:
        return self.session.exec(select(User).where(User.username == username)).first()

    def get_by_email(self, email: str) -> User | None:
        return self.session.exec(select(User).where(User.email == email)).first()

    def find_first_admin(self) -> User | None:
        return self.session.exec(select(User).where(User.is_admin).limit(1)).first()

    def list_all(self) -> list[User]:
        return list(self.session.exec(select(User)).all())

    def toggle_admin(self, user_id: int) -> User:
        user = self.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        user.is_admin = not user.is_admin
        return self.update(user)

    def toggle_active(self, user_id: int) -> User:
        user = self.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        user.is_active = not user.is_active
        return self.update(user)
