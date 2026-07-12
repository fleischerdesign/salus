from collections.abc import Callable
from typing import TYPE_CHECKING

from sqlmodel import Session, SQLModel

from salus.models import MetricType
from salus.models.api_token import ApiToken
from salus.models.asymmetric_share import AsymmetricShare, ShareRecipient
from salus.models.circadian import CircadianProfile
from salus.models.dashboard import DashboardWidget
from salus.models.goal import Goal
from salus.models.measurement import Measurement
from salus.models.notification import Notification
from salus.models.user import User
from salus.models.workout import Exercise, WorkoutLogEntry, WorkoutPlan, WorkoutPlanExercise, WorkoutSession

if TYPE_CHECKING:
    from salus.schemas.sync import SyncOperation

ENTITY_REGISTRY: dict[str, type[SQLModel]] = {
    "metric_type": MetricType,
    "measurement": Measurement,
    "goal": Goal,
    "circadian_profile": CircadianProfile,
    "exercise": Exercise,
    "workout_plan": WorkoutPlan,
    "workout_plan_exercise": WorkoutPlanExercise,
    "workout_session": WorkoutSession,
    "workout_log_entry": WorkoutLogEntry,
    "dashboard_widget": DashboardWidget,
    "notification": Notification,
    "share_recipient": ShareRecipient,
    "asymmetric_share": AsymmetricShare,
    "user": User,
    "api_token": ApiToken,
}

ValidatorFn = Callable[..., str | None]

_SAFE_USER_UPDATE_FIELDS = {"theme", "locale", "display_name", "onboarding_dismissed"}


def _validate_user_update(
    session: Session, current_user: User, data: dict, op: "SyncOperation"
) -> str | None:
    if op.type == "create":
        return "User creation via sync push is not allowed. Use the authentication flow."
    if op.type == "delete":
        return "User deletion via sync push is not allowed. Use the admin interface."

    blocked = [k for k in data if k not in _SAFE_USER_UPDATE_FIELDS]
    if blocked:
        return f"Cannot update user fields via sync push: {', '.join(blocked)}"

    instance = session.get(User, op.id)
    if not instance or instance.id != current_user.id:
        return "Cannot update another user's profile"

    return None


_SAFE_API_TOKEN_UPDATE_FIELDS = {"is_active"}


def _validate_api_token_update(
    session: Session, current_user: User, data: dict, op: "SyncOperation"
) -> str | None:
    if op.type == "create":
        return "API token creation via sync push is not allowed. Use POST /api/v1/settings/tokens."

    blocked = [k for k in data if k not in _SAFE_API_TOKEN_UPDATE_FIELDS]
    if blocked:
        return f"Cannot update API token fields via sync push: {', '.join(blocked)}"

    instance = session.get(ApiToken, op.id)
    if not instance:
        return f"API token not found: {op.id}"
    if instance.user_id != current_user.id:
        return "Cannot modify another user's API token"

    return None


ENTITY_VALIDATORS: dict[str, ValidatorFn] = {
    "user": _validate_user_update,
    "api_token": _validate_api_token_update,
}
