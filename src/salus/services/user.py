from salus.exceptions import ConflictError, NotFoundError
from salus.models.metric_definition import MetricDefinition, MetricGroup
from salus.models.metric_preference import UserMetricPreference
from salus.models.user import User
from salus.models.user_identity import UserIdentity
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services._helpers import uid
from salus.services.metric_type_mapping import METRIC_DEFINITIONS, METRIC_GROUPS, DEFAULT_METRIC_PREFERENCES
from salus.services.password import hash_password, verify_password


class UserService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def _is_first_user(self) -> bool:
        all_users = self.uow.users.list_all()
        return len(all_users) == 0

    def _seed_default_metric_types(self, user_id: str) -> None:
        session = self.uow.session

        # Seed global metric groups (idempotent)
        for group_data in METRIC_GROUPS:
            if session.get(MetricGroup, group_data["key"]) is None:
                session.add(MetricGroup(
                    key=group_data["key"], name=group_data["name"],
                    icon=group_data["icon"], input_mode=group_data.get("input_mode", "individual")
                ))

        # Seed global metric definitions (idempotent)
        for md_data in METRIC_DEFINITIONS:
            existing = session.get(MetricDefinition, md_data["code"])
            if existing is None:
                session.add(MetricDefinition(**md_data))
            else:
                # Update mutable fields for existing definitions (e.g. source_data_type)
                changed = False
                for key in ("source_data_type", "group_key", "unit", "name", "sort_order"):
                    if key in md_data and getattr(existing, key) != md_data[key]:
                        setattr(existing, key, md_data[key])
                        changed = True
                if changed:
                    session.add(existing)

        # Seed user preferences
        for p in DEFAULT_METRIC_PREFERENCES:
            existing = self.uow.metric_preferences.find_by_user_and_code(
                user_id, p["code"]
            )
            if existing is None:
                self.uow.metric_preferences.create(
                    UserMetricPreference(
                        user_id=user_id,
                        metric_code=p["code"],
                        enabled=p.get("enabled", True),
                        color=p.get("color", "#4f46e5"),
                        icon=p.get("icon", "monitoring"),
                        widget_size=p.get("widget_size", "medium"),
                        widget_enabled=p.get("widget_enabled", False),
                        position=p.get("position", 0),
                    )
                )

    def get_by_id(self, user_id: str) -> User:
        user = self.uow.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")
        return user

    def get_by_username(self, username: str) -> User | None:
        return self.uow.users.get_by_username(username)

    def get_by_email(self, email: str) -> User | None:
        return self.uow.users.get_by_email(email)

    def register(
        self,
        username: str,
        password: str,
        email: str | None = None,
        display_name: str | None = None,
    ) -> User:
        existing = self.uow.users.get_by_username(username)
        if existing is not None:
            raise ConflictError(f"Username '{username}' already taken")

        if email:
            existing_email = self.uow.users.get_by_email(email)
            if existing_email is not None:
                raise ConflictError(f"Email '{email}' already registered")

        user = User(
            username=username,
            password_hash=hash_password(password),
            email=email,
            display_name=display_name or username,
            is_admin=self._is_first_user(),
        )
        user = self.uow.users.create(user)

        self.uow.identities.create(
            UserIdentity(
                user_id=uid(user),
                provider="local",
                provider_user_id=username,
            )
        )
        self._seed_default_metric_types(uid(user))
        return user

    def register_with_identity(
        self,
        provider: str,
        provider_user_id: str,
        username: str | None = None,
        email: str | None = None,
        display_name: str | None = None,
    ) -> User:
        existing = self.uow.identities.get_by_provider_user_id(
            provider, provider_user_id
        )
        if existing is not None:
            return self.get_by_id(existing.user_id)

        if email:
            user_by_email = self.uow.users.get_by_email(email)
            if user_by_email is not None:
                self.uow.identities.create(
                    UserIdentity(
                        user_id=uid(user_by_email),
                        provider=provider,
                        provider_user_id=provider_user_id,
                    )
                )
                self._seed_default_metric_types(uid(user_by_email))
                return user_by_email

        derived_username = username or f"{provider}_{provider_user_id}"
        derived_display = display_name or email or derived_username

        user = User(
            username=derived_username,
            password_hash=None,
            email=email,
            display_name=derived_display,
            is_admin=self._is_first_user(),
        )
        user = self.uow.users.create(user)

        self.uow.identities.create(
            UserIdentity(
                user_id=uid(user),
                provider=provider,
                provider_user_id=provider_user_id,
            )
        )
        self._seed_default_metric_types(uid(user))
        return user

    def change_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> User:
        user = self.get_by_id(user_id)
        if user.password_hash and not verify_password(old_password, user.password_hash):
            raise ConflictError("Current password is incorrect")

        user.password_hash = hash_password(new_password)
        return self.uow.users.update(user)

    def list_identities(self, user_id: str) -> list[UserIdentity]:
        return self.uow.identities.list_by_user(user_id)

    def set_theme(self, user_id: str, theme: str) -> User:
        user = self.get_by_id(user_id)
        user.theme = theme
        return self.uow.users.update(user)

    def update_profile(
        self,
        user_id: str,
        display_name: str | None = None,
        height_cm: float | None = None,
    ) -> User:
        user = self.get_by_id(user_id)
        if display_name is not None:
            user.display_name = display_name
        if height_cm is not None:
            user.height_cm = height_cm
        return self.uow.users.update(user)

    def dismiss_onboarding(self, user_id: str) -> None:
        user = self.get_by_id(user_id)
        user.onboarding_dismissed = True
        self.uow.users.update(user)
