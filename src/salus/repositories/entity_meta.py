from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from sqlmodel import Session, SQLModel, select

from salus.models.api_token import ApiToken
from salus.models.asymmetric_share import AsymmetricShare, ShareRecipient
from salus.models.circadian import CircadianProfile
from salus.models.dashboard import DashboardWidget
from salus.models.goal import Goal
from salus.models.insight import Insight
from salus.models.measurement import Measurement
from salus.models.metric_definition import MetricDefinition, MetricGroup
from salus.models.metric_preference import UserMetricPreference
from salus.models.notification import Notification
from salus.models.sharing import FederatedAccessLog, LeaderboardGroup, LeaderboardMember, SharingRelationship
from salus.models.user import User
from salus.models.workout import Exercise, Program, ProgramWorkout, WorkoutSet, Workout, WorkoutExercise, WorkoutSession
from salus.models.habit import Habit, HabitLog
from salus.models.mood import MoodTag, MoodEntry
from salus.models.journal import JournalEntry
from salus.models.achievement import AchievementDefinition, UserAchievement
from salus.models.medication import (
    Medication,
    MedicationInventory,
    MedicationLog,
    MedicationSchedule,
)
from salus.models.food import (
    FoodItem,
    Meal,
    MealItem,
    Recipe,
    RecipeIngredient,
)
from salus.models.user_source_preference import UserSourcePreference
from salus.models.user_source_status import UserSourceStatus
from salus.models.lab import LabMarker, LabPanel, LabResult
from salus.models.fasting import FastingProtocol, FastingSession
from salus.models.data_quality import DataQualityFlag

if TYPE_CHECKING:
    from salus.schemas.sync import SyncOperation

# ── Single source of truth ──


@dataclass
class EntityMeta:
    name: str
    model: type[SQLModel]
    strategy: str = "user_scoped"
    owner_field: str | None = None
    parent_field: str | None = None
    parent_model: type[SQLModel] | None = None
    parent_owner_field: str | None = None
    timestamp_field: str | None = None
    no_soft_delete: bool = False
    batch_size: int = 500


# Strategies the client may write via sync push and auto-CRUD. Everything else
# (global reference data, append-only server records) is read-only.
WRITABLE_STRATEGIES: frozenset[str] = frozenset(
    {"user_scoped", "shared_nullable", "relational"}
)


ENTITY_META: list[EntityMeta] = [
    EntityMeta(name="metric_group", model=MetricGroup, strategy="global", batch_size=500),
    EntityMeta(name="metric_definition", model=MetricDefinition, strategy="global", batch_size=500),
    EntityMeta(name="user_metric_preference", model=UserMetricPreference, batch_size=500),
    EntityMeta(name="user_source_preference", model=UserSourcePreference, batch_size=500),
    EntityMeta(name="user_source_status", model=UserSourceStatus, batch_size=500),
    EntityMeta(name="measurement", model=Measurement, batch_size=2000),
    EntityMeta(name="goal", model=Goal, batch_size=500),
    EntityMeta(name="circadian_profile", model=CircadianProfile, batch_size=500),
    EntityMeta(name="exercise", model=Exercise, strategy="shared_nullable", batch_size=500),
    EntityMeta(name="workout", model=Workout, batch_size=500),
    EntityMeta(
        name="workout_exercise", model=WorkoutExercise, strategy="relational",
        parent_field="workout_id", parent_model=Workout, parent_owner_field="user_id", batch_size=500,
    ),
    EntityMeta(name="program", model=Program, batch_size=500),
    EntityMeta(
        name="program_workout", model=ProgramWorkout, strategy="relational",
        parent_field="program_id", parent_model=Program, parent_owner_field="user_id", batch_size=500,
    ),
    EntityMeta(name="workout_session", model=WorkoutSession, batch_size=500),
    EntityMeta(
        name="workout_set", model=WorkoutSet, strategy="relational",
        parent_field="session_id", parent_model=WorkoutSession, parent_owner_field="user_id", batch_size=500,
    ),
    EntityMeta(name="insight", model=Insight, batch_size=500),
    EntityMeta(name="notification", model=Notification, batch_size=500),
    EntityMeta(name="dashboard_widget", model=DashboardWidget, batch_size=500),
    EntityMeta(name="sharing_relationship", model=SharingRelationship, owner_field="owner_id", batch_size=500),
    EntityMeta(name="leaderboard_group", model=LeaderboardGroup, strategy="global", batch_size=500),
    EntityMeta(name="leaderboard_member", model=LeaderboardMember, strategy="global", batch_size=500),
    EntityMeta(name="share_recipient", model=ShareRecipient, batch_size=500),
    EntityMeta(name="asymmetric_share", model=AsymmetricShare, batch_size=500),
    EntityMeta(name="api_token", model=ApiToken, strategy="append_only", timestamp_field="created_at", no_soft_delete=True, batch_size=500),
    EntityMeta(name="federated_access_log", model=FederatedAccessLog, strategy="append_only", owner_field="owner_id", timestamp_field="accessed_at", no_soft_delete=True, batch_size=500),
    EntityMeta(name="user", model=User, strategy="user_scoped", batch_size=500),
    EntityMeta(name="habit", model=Habit, batch_size=500),
    EntityMeta(name="habit_log", model=HabitLog, batch_size=2000),
    EntityMeta(name="mood_tag", model=MoodTag, strategy="global", no_soft_delete=True, batch_size=500),
    EntityMeta(name="mood_entry", model=MoodEntry, batch_size=500),
    EntityMeta(name="journal_entry", model=JournalEntry, batch_size=500),
    EntityMeta(name="achievement_definition", model=AchievementDefinition, strategy="global", no_soft_delete=True, batch_size=500),
    EntityMeta(name="user_achievement", model=UserAchievement, no_soft_delete=True, batch_size=500),
    EntityMeta(name="medication", model=Medication, batch_size=500),
    EntityMeta(name="medication_schedule", model=MedicationSchedule, batch_size=500),
    EntityMeta(name="medication_log", model=MedicationLog, batch_size=2000),
    EntityMeta(name="medication_inventory", model=MedicationInventory, batch_size=500),
    EntityMeta(name="food_item", model=FoodItem, strategy="shared_nullable", batch_size=2000),
    EntityMeta(name="meal", model=Meal, batch_size=500),
    EntityMeta(name="meal_item", model=MealItem, batch_size=2000),
    EntityMeta(name="recipe", model=Recipe, batch_size=500),
    EntityMeta(name="recipe_ingredient", model=RecipeIngredient, batch_size=500),
    EntityMeta(name="lab_marker", model=LabMarker, strategy="global", no_soft_delete=True, batch_size=500),
    EntityMeta(name="lab_panel", model=LabPanel, batch_size=500),
    EntityMeta(name="lab_result", model=LabResult, batch_size=2000),
    EntityMeta(name="fasting_session", model=FastingSession, batch_size=500),
    EntityMeta(name="fasting_protocol", model=FastingProtocol, batch_size=500),
    EntityMeta(name="data_quality_flag", model=DataQualityFlag, strategy="append_only", owner_field="user_id", timestamp_field="created_at", no_soft_delete=True, batch_size=500),
]

# ── Derived mappings ──

ENTITY_REGISTRY: dict[str, type[SQLModel]] = {
    e.name: e.model for e in ENTITY_META
}

ENTITY_META_BY_NAME: dict[str, EntityMeta] = {
    e.name: e for e in ENTITY_META
}

SYNC_ENTITY_SPECS: list[EntityMeta] = [
    e for e in ENTITY_META if e.name != "user"
]

DELTA_ENTITY_SPECS: list[EntityMeta] = [
    e for e in ENTITY_META
    if e.strategy in ("user_scoped", "shared_nullable", "relational", "global")
    and e.name != "user"
]

APPEND_ONLY_DELTA_SPECS: list[EntityMeta] = [
    e for e in ENTITY_META if e.strategy == "append_only"
]

# ── Validators ──

ValidatorFn = Callable[..., str | None]

# User profile fields the client may write via sync push and the update_profile
# command. Single source of truth — imported by services/commands/account.py.
SAFE_PROFILE_FIELDS = {
    "theme",
    "locale",
    "timezone",
    "display_name",
    "onboarding_dismissed",
    "colorblind",
    "accent_hue",
    "dq_notify_hard_bound",
    "dq_notify_cross_source",
    "dq_notify_anomaly",
}


def _validate_user_update(
    session: Session, current_user: User, data: dict, op: "SyncOperation",
) -> str | None:
    if op.type == "create":
        return "User creation via sync push is not allowed. Use the authentication flow."
    if op.type == "delete":
        return "User deletion via sync push is not allowed. Use the admin interface."
    blocked = [k for k in data if k not in SAFE_PROFILE_FIELDS]
    if blocked:
        return f"Cannot update user fields via sync push: {', '.join(blocked)}"
    instance = session.get(User, op.id)
    if not instance or instance.id != current_user.id:
        return "Cannot update another user's profile"
    return None


def _validate_exercise_create(
    session: Session, _current_user: User, data: dict, op: "SyncOperation",
) -> str | None:
    if op.type != "create":
        return None
    name = (data.get("name") or "").strip()
    if not name:
        return None
    stmt = select(Exercise).where(
        Exercise.name == name,
        Exercise.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    )
    existing = session.exec(stmt).first()
    if existing:
        return f"Exercise '{name}' already exists"
    return None


def _validate_metric_preference_create(
    session: Session, current_user: User, data: dict, op: "SyncOperation",
) -> str | None:
    if op.type != "create":
        return None
    metric_code = data.get("metric_code")
    if metric_code is None:
        return None
    if session.get(MetricDefinition, metric_code) is None:
        return f"Unknown metric_code: {metric_code}"
    existing = session.exec(
        select(UserMetricPreference).where(
            UserMetricPreference.user_id == current_user.id,
            UserMetricPreference.metric_code == metric_code,
        )
    ).first()
    if existing:
        return f"Metric preference for '{metric_code}' already exists"
    return None


def _validate_measurement_create(
    session: Session, _current_user: User, data: dict, op: "SyncOperation",
) -> str | None:
    if op.type != "create":
        return None
    metric_code = data.get("metric_code")
    if not metric_code:
        return None
    if session.get(MetricDefinition, metric_code) is None:
        return f"Unknown metric_code: {metric_code}"
    return None


def _readonly_validator(label: str) -> ValidatorFn:
    def _reject(
        _session: Session, _current_user: User, _data: dict, _op: "SyncOperation",
    ) -> str:
        return f"{label} are server-managed and cannot be written via sync push"

    return _reject


ENTITY_VALIDATORS: dict[str, ValidatorFn] = {
    "user": _validate_user_update,
    "exercise": _validate_exercise_create,
    "user_metric_preference": _validate_metric_preference_create,
    "measurement": _validate_measurement_create,
    "user_achievement": _readonly_validator("Achievements"),
    "insight": _readonly_validator("Insights"),
    "notification": _readonly_validator("Notifications"),
    "sharing_relationship": _readonly_validator("Sharing relationships"),
    "share_recipient": _readonly_validator("Share recipients"),
    "asymmetric_share": _readonly_validator("Asymmetric shares"),
}

# ── After-write hooks ──
#
# Optional per-entity callbacks run by the WritePipeline after a successful
# create/update (never delete) within the same transaction. They must not raise:
# the write path treats them as best-effort (e.g. data-quality flagging) and
# isolates failures from the primary write.

AfterWriteFn = Callable[..., None]

ENTITY_AFTER_WRITE: dict[str, AfterWriteFn] = {}
