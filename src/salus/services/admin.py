import os

from salus.config import settings as app_settings
from salus.exceptions import ConflictError, NotFoundError
from salus.models.api_token import ApiToken
from salus.models.goal import Goal
from salus.models.measurement import Measurement
from salus.models.metric_definition import MetricDefinition
from salus.models.user import User
from salus.repositories.unit_of_work import IUnitOfWork
from sqlmodel import func, select


def admin_user_list(s, exclude_user_id: str | None = None) -> list[dict]:
    measurement_subq = (
        select(func.count())
        .select_from(Measurement)
        .where(
            Measurement.user_id == User.id,
            Measurement.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        .correlate(User)
        .scalar_subquery()
        .label("measurement_count")
    )
    goal_subq = (
        select(func.count())
        .select_from(Goal)
        .where(Goal.user_id == User.id, Goal.deleted_at.is_(None))  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        .correlate(User)
        .scalar_subquery()
        .label("goal_count")
    )

    stmt = select(  # pyright: ignore[reportCallIssue]
        User.id,
        User.username,
        User.email,
        User.display_name,
        User.is_admin,
        User.is_active,
        User.created_at,
        measurement_subq,
        goal_subq,
    )
    if exclude_user_id is not None:
        stmt = stmt.where(User.id != exclude_user_id)

    rows = s.exec(stmt).all()

    return [
        {
            "id": r[0],
            "username": r[1],
            "email": r[2],
            "display_name": r[3],
            "is_admin": r[4],
            "is_active": r[5],
            "created_at": r[6],
            "measurement_count": r[7] or 0,
            "goal_count": r[8] or 0,
        }
        for r in rows
        if r[0] is not None
    ]


def _format_bytes(num_bytes: int) -> str:
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} MB"
    if num_bytes >= 1024:
        return f"{num_bytes / 1024:.1f} KB"
    return f"{num_bytes} B"


def _system_counts(s) -> dict:
    return {
        "total_users": s.scalar(select(func.count()).select_from(User)) or 0,
        "total_measurements": s.scalar(
            select(func.count())
            .select_from(Measurement)
            .where(Measurement.deleted_at.is_(None))  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        or 0,
        "total_metric_types": s.scalar(
            select(func.count()).select_from(MetricDefinition)
        )
        or 0,
        "total_goals": s.scalar(select(func.count()).select_from(Goal)) or 0,
    }


def admin_system_stats(s) -> dict:
    db_path = app_settings.database_url.replace("sqlite:///", "")
    db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    return {
        "key": "global",
        **_system_counts(s),
        "db_size": _format_bytes(db_size_bytes),
    }


class AdminService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def get_storage_stats(self) -> dict:
        db_path = app_settings.database_url.replace("sqlite:///", "")
        db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0

        s = self.uow.session
        counts = _system_counts(s)
        return {
            "db_size": _format_bytes(db_size_bytes),
            "db_path": db_path,
            "row_counts": {
                "Users": counts["total_users"],
                "Measurements": counts["total_measurements"],
                "Metric Types": counts["total_metric_types"],
                "Goals": counts["total_goals"],
                "API Tokens": s.scalar(
                    select(func.count()).select_from(ApiToken).where(ApiToken.is_active)
                )
                or 0,
            },
        }

    def get_system_stats(self) -> dict:
        return _system_counts(self.uow.session)

    def list_users_with_stats(self) -> list[dict]:
        return admin_user_list(self.uow.session)

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
