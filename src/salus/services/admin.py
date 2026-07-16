import os

from salus.config import settings as app_settings
from salus.exceptions import ConflictError, NotFoundError
from salus.models.api_token import ApiToken
from salus.models.user import User
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services._helpers import uid


class AdminService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def get_storage_stats(self) -> dict:
        db_path = app_settings.database_url.replace("sqlite:///", "")
        db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        if db_size_bytes >= 1024 * 1024:
            db_size_str = f"{db_size_bytes / (1024 * 1024):.1f} MB"
        elif db_size_bytes >= 1024:
            db_size_str = f"{db_size_bytes / 1024:.1f} KB"
        else:
            db_size_str = f"{db_size_bytes} B"

        return {
            "db_size": db_size_str,
            "db_path": db_path,
            "row_counts": {
                "Users": len(self.uow.users.list_all()),
                "Measurements": len(self.uow.measurements.find_all()),
                "Metric Types": len(self.uow.metric_definitions.find_all()),
                "Goals": len(self.uow.goals.find_all_goals()),
                "API Tokens": len(self.uow.api_tokens.list_all_active()),
            },
        }

    def get_system_stats(self) -> dict:
        users = self.uow.users.list_all()
        total_users = len(users)
        total_measurements = len(self.uow.measurements.find_all())
        total_metric_types = len(self.uow.metric_definitions.find_all())
        goals = self.uow.goals.find_all_goals()
        total_goals = len(goals)
        return {
            "total_users": total_users,
            "total_measurements": total_measurements,
            "total_metric_types": total_metric_types,
            "total_goals": total_goals,
        }

    def list_users_with_stats(self) -> list[dict]:
        users = self.uow.users.list_all()
        result: list[dict] = []
        for user in users:
            user_id = uid(user) if user.id is not None else ""
            measurements = self.uow.measurements.find_all(user_id=user_id)
            goals = self.uow.goals.find_by_user(user_id)
            result.append(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "display_name": user.display_name,
                    "is_admin": user.is_admin,
                    "is_active": user.is_active,
                    "created_at": user.created_at,
                    "measurement_count": len(measurements),
                    "goal_count": len(goals),
                }
            )
        return result

    def toggle_admin(self, user_id: str) -> User:
        return self.uow.users.toggle_admin(user_id)

    def toggle_active(self, user_id: str) -> User:
        return self.uow.users.toggle_active(user_id)

    def list_all_tokens(self) -> list[ApiToken]:
        return self.uow.api_tokens.list_all_active()

    def revoke_token(self, token_id: str) -> None:
        token = self.uow.api_tokens.get_by_id(token_id)
        if token is not None:
            token.is_active = False
            self.uow.api_tokens.update(token)

    def delete_user(self, user_id: str, deleted_by: str) -> None:
        if user_id == deleted_by:
            raise ConflictError("Cannot delete your own account")

        user = self.uow.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")

        for token in self.uow.api_tokens.find_all_by_user(user_id):
            self.uow.api_tokens.delete(token)

        for widget in self.uow.dashboard_widgets.find_by_user(user_id):
            self.uow.dashboard_widgets.delete(widget)

        self.uow.users.delete(user)

    def get_user_detail(self, user_id: str) -> dict:
        user = self.uow.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "display_name": user.display_name,
            "is_admin": user.is_admin,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "identities": user.identities,
            "metrics": user.metric_preferences,
            "recent_entries": self.uow.measurements.find_all(
                user_id=user_id, limit=10
            ),
            "goals": self.uow.goals.find_by_user(user_id),
            "tokens": self.uow.api_tokens.find_all_by_user(user_id),
        }
