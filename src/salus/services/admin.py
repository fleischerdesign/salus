import os

from salus.config import settings as app_settings
from salus.exceptions import ConflictError, NotFoundError
from salus.models.api_token import ApiToken
from salus.models.user import User
from salus.repositories.protocols import (
    IApiTokenRepository,
    IDashboardWidgetRepository,
    IGoalRepository,
    IMeasurementRepository,
    IMetricTypeRepository,
    IUserRepository,
)
from salus.services._helpers import uid


class AdminService:
    def __init__(
        self,
        user_repo: IUserRepository,
        metric_type_repo: IMetricTypeRepository,
        measurement_repo: IMeasurementRepository,
        api_token_repo: IApiTokenRepository,
        goal_repo: IGoalRepository,
        dashboard_widget_repo: IDashboardWidgetRepository,
    ) -> None:
        self._user_repo = user_repo
        self._metric_type_repo = metric_type_repo
        self._measurement_repo = measurement_repo
        self._api_token_repo = api_token_repo
        self._goal_repo = goal_repo
        self._dashboard_widget_repo = dashboard_widget_repo

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
                "Users": len(self._user_repo.list_all()),
                "Measurements": len(self._measurement_repo.find_all()),
                "Metric Types": len(self._metric_type_repo.find_all()),
                "Goals": len(self._goal_repo.find_all_goals()),
                "API Tokens": len(self._api_token_repo.list_all_active()),
            },
        }

    def get_system_stats(self) -> dict:
        users = self._user_repo.list_all()
        total_users = len(users)
        total_measurements = len(self._measurement_repo.find_all())
        total_metric_types = len(self._metric_type_repo.find_all())
        goals = self._goal_repo.find_all_goals()
        total_goals = len(goals)
        return {
            "total_users": total_users,
            "total_measurements": total_measurements,
            "total_metric_types": total_metric_types,
            "total_goals": total_goals,
        }

    def list_users_with_stats(self) -> list[dict]:
        users = self._user_repo.list_all()
        result: list[dict] = []
        for user in users:
            user_id = uid(user) if user.id is not None else 0
            measurements = self._measurement_repo.find_all(user_id=user_id)
            goals = self._goal_repo.find_by_user(user_id)
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

    def toggle_admin(self, user_id: int) -> User:
        return self._user_repo.toggle_admin(user_id)

    def toggle_active(self, user_id: int) -> User:
        return self._user_repo.toggle_active(user_id)

    def list_all_tokens(self) -> list[ApiToken]:
        return self._api_token_repo.list_all_active()

    def revoke_token(self, token_id: int) -> None:
        token = self._api_token_repo.get_by_id(token_id)
        if token is not None:
            token.is_active = False
            self._api_token_repo.update(token)

    def delete_user(self, user_id: int, deleted_by: int) -> None:
        if user_id == deleted_by:
            raise ConflictError("Cannot delete your own account")

        user = self._user_repo.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"User {user_id} not found")

        for token in self._api_token_repo.find_all_by_user(user_id):
            self._api_token_repo.delete(token)

        for widget in self._dashboard_widget_repo.find_by_user(user_id):
            self._dashboard_widget_repo.delete(widget)

        self._user_repo.delete(user)

    def get_user_detail(self, user_id: int) -> dict:
        user = self._user_repo.get_by_id(user_id)
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
            "metrics": user.metric_types,
            "recent_entries": self._measurement_repo.find_all(
                user_id=user_id, limit=10
            ),
            "goals": self._goal_repo.find_by_user(user_id),
            "tokens": self._api_token_repo.find_all_by_user(user_id),
        }
