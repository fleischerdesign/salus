from dataclasses import dataclass

from sqlmodel import SQLModel

from salus.models import MetricType
from salus.models.api_token import ApiToken
from salus.models.asymmetric_share import AsymmetricShare, ShareRecipient
from salus.models.circadian import CircadianProfile
from salus.models.dashboard import DashboardWidget
from salus.models.goal import Goal
from salus.models.insight import Insight
from salus.models.measurement import Measurement
from salus.models.notification import Notification
from salus.models.sharing import FederatedAccessLog, LeaderboardGroup, LeaderboardMember, SharingRelationship
from salus.models.workout import Exercise, WorkoutLogEntry, WorkoutPlan, WorkoutPlanExercise, WorkoutSession


@dataclass
class SyncEntitySpec:
    name: str
    model: type[SQLModel]
    strategy: str

    owner_field: str | None = None
    parent_field: str | None = None
    parent_model: type[SQLModel] | None = None
    parent_owner_field: str | None = None
    timestamp_field: str | None = None
    no_soft_delete: bool = False
    batch_size: int = 500


SYNC_ENTITY_SPECS: list[SyncEntitySpec] = [
    SyncEntitySpec(name="metric_type", model=MetricType, strategy="user_scoped", batch_size=500),
    SyncEntitySpec(name="measurement", model=Measurement, strategy="user_scoped", batch_size=2000),
    SyncEntitySpec(name="goal", model=Goal, strategy="user_scoped", batch_size=500),
    SyncEntitySpec(name="circadian_profile", model=CircadianProfile, strategy="user_scoped", batch_size=500),
    SyncEntitySpec(
        name="exercise", model=Exercise, strategy="shared_nullable", batch_size=500,
    ),
    SyncEntitySpec(name="workout_plan", model=WorkoutPlan, strategy="user_scoped", batch_size=500),
    SyncEntitySpec(
        name="workout_plan_exercise", model=WorkoutPlanExercise, strategy="relational",
        parent_field="plan_id", parent_model=WorkoutPlan, parent_owner_field="user_id", batch_size=500,
    ),
    SyncEntitySpec(name="workout_session", model=WorkoutSession, strategy="user_scoped", batch_size=500),
    SyncEntitySpec(
        name="workout_log_entry", model=WorkoutLogEntry, strategy="relational",
        parent_field="session_id", parent_model=WorkoutSession, parent_owner_field="user_id", batch_size=500,
    ),
    SyncEntitySpec(name="insight", model=Insight, strategy="user_scoped", batch_size=500),
    SyncEntitySpec(name="notification", model=Notification, strategy="user_scoped", batch_size=500),
    SyncEntitySpec(name="dashboard_widget", model=DashboardWidget, strategy="user_scoped", batch_size=500),
    SyncEntitySpec(
        name="sharing_relationship", model=SharingRelationship, strategy="user_scoped",
        owner_field="owner_id", batch_size=500,
    ),
    SyncEntitySpec(name="leaderboard_group", model=LeaderboardGroup, strategy="global", batch_size=500),
    SyncEntitySpec(name="leaderboard_member", model=LeaderboardMember, strategy="global", batch_size=500),
    SyncEntitySpec(name="share_recipient", model=ShareRecipient, strategy="user_scoped", batch_size=500),
    SyncEntitySpec(name="asymmetric_share", model=AsymmetricShare, strategy="user_scoped", batch_size=500),
    SyncEntitySpec(
        name="api_token", model=ApiToken, strategy="append_only",
        timestamp_field="created_at", no_soft_delete=True, batch_size=500,
    ),
    SyncEntitySpec(
        name="federated_access_log", model=FederatedAccessLog, strategy="append_only",
        owner_field="owner_id", timestamp_field="accessed_at", no_soft_delete=True, batch_size=500,
    ),
]

DELTA_ENTITY_SPECS: list[SyncEntitySpec] = [
    s for s in SYNC_ENTITY_SPECS
    if s.strategy in ("user_scoped", "shared_nullable", "relational", "global")
]

APPEND_ONLY_DELTA_SPECS: list[SyncEntitySpec] = [
    s for s in SYNC_ENTITY_SPECS
    if s.strategy == "append_only"
]
