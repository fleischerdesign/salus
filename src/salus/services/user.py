from salus.exceptions import ConflictError, NotFoundError
from salus.models.user import User
from salus.models.user_identity import UserIdentity
from salus.repositories.user import UserRepository
from salus.repositories.user_identity import UserIdentityRepository
from salus.services._helpers import uid
from salus.services.password import hash_password, verify_password


class UserService:
    def __init__(self, repo: UserRepository, identity_repo: UserIdentityRepository) -> None:
        self.repo = repo
        self.identity_repo = identity_repo

    def get_by_id(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        return user

    def get_by_username(self, username: str) -> User | None:
        return self.repo.get_by_username(username)

    def get_by_email(self, email: str) -> User | None:
        return self.repo.get_by_email(email)

    def register(
        self,
        username: str,
        password: str,
        email: str | None = None,
        display_name: str | None = None,
    ) -> User:
        existing = self.repo.get_by_username(username)
        if existing is not None:
            raise ConflictError(f"Username '{username}' already taken")

        if email:
            existing_email = self.repo.get_by_email(email)
            if existing_email is not None:
                raise ConflictError(f"Email '{email}' already registered")

        user = User(
            username=username,
            password_hash=hash_password(password),
            email=email,
            display_name=display_name or username,
        )
        user = self.repo.create(user)

        self.identity_repo.create(
            UserIdentity(
                user_id=uid(user),
                provider="local",
                provider_user_id=username,
            )
        )
        return user

    def register_with_identity(
        self,
        provider: str,
        provider_user_id: str,
        username: str | None = None,
        email: str | None = None,
        display_name: str | None = None,
    ) -> User:
        existing = self.identity_repo.get_by_provider_user_id(provider, provider_user_id)
        if existing is not None:
            return self.get_by_id(existing.user_id)

        if email:
            user_by_email = self.repo.get_by_email(email)
            if user_by_email is not None:
                self.identity_repo.create(
                    UserIdentity(
                        user_id=uid(user_by_email),
                        provider=provider,
                        provider_user_id=provider_user_id,
                    )
                )
                return user_by_email

        derived_username = username or f"{provider}_{provider_user_id}"
        derived_display = display_name or email or derived_username

        user = User(
            username=derived_username,
            password_hash=None,
            email=email,
            display_name=derived_display,
        )
        user = self.repo.create(user)

        self.identity_repo.create(
            UserIdentity(
                user_id=uid(user),
                provider=provider,
                provider_user_id=provider_user_id,
            )
        )
        return user

    def change_password(self, user_id: int, old_password: str, new_password: str) -> User:
        user = self.get_by_id(user_id)
        if user.password_hash and not verify_password(old_password, user.password_hash):
            raise ConflictError("Current password is incorrect")

        user.password_hash = hash_password(new_password)
        return self.repo.update(user)

    def list_identities(self, user_id: int) -> list[UserIdentity]:
        return self.identity_repo.list_by_user(user_id)
