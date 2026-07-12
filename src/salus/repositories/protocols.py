from datetime import datetime
from typing import Protocol, TypeVar, runtime_checkable

from salus.models.api_token import ApiToken
from salus.models.dashboard import DashboardWidget
from salus.models.goal import Goal
from salus.models.insight import Insight
from salus.models.measurement import Measurement
from salus.models import MetricType
from salus.models.system_config import SystemConfig
from salus.models.user import User
from salus.models.user_identity import UserIdentity
from salus.models.sharing import (
    FederatedAccessLog,
    FederatedMeasurementCache,
    LeaderboardGroup,
    LeaderboardMember,
    SharingRelationship,
)
from salus.models.workout import Exercise, WorkoutPlan, WorkoutSession, WorkoutPlanExercise, WorkoutLogEntry
from salus.models.asymmetric_share import ShareRecipient, AsymmetricShare
from salus.models.circadian import CircadianProfile
from salus.models.notification import Notification
from salus.models.sync_push_log import SyncPushLog

T = TypeVar("T")


@runtime_checkable
class IRepository(Protocol[T]):
    def get_by_id(self, id: int) -> T | None: ...

    def create(self, obj: T) -> T: ...

    def update(self, obj: T) -> T: ...

    def delete(self, obj: T) -> None: ...

    def add(self, obj: T) -> None: ...

    def add_all(self, objs: list[T]) -> None: ...

    def commit(self) -> None: ...


@runtime_checkable
class IUserRepository(IRepository[User], Protocol):
    def get_by_username(self, username: str) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def find_first_admin(self) -> User | None: ...

    def list_all(self) -> list[User]: ...

    def toggle_admin(self, user_id: int) -> User: ...

    def toggle_active(self, user_id: int) -> User: ...


@runtime_checkable
class IUserIdentityRepository(IRepository[UserIdentity], Protocol):
    def get_by_provider_user_id(
        self, provider: str, provider_user_id: str
    ) -> UserIdentity | None: ...

    def list_by_user(self, user_id: int) -> list[UserIdentity]: ...


@runtime_checkable
class IMeasurementRepository(IRepository[Measurement], Protocol):
    def find_by_metric_type(
        self, metric_type_id: int, user_id: int | None = None
    ) -> list[Measurement]: ...

    def find_all(
        self,
        user_id: int | None = None,
        data_types: list[str] | None = None,
        sources: list[str] | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
    ) -> list[Measurement]: ...

    def find_latest(
        self, data_type: str, user_id: int | None = None
    ) -> Measurement | None: ...

    def upsert_all(self, records: list[Measurement]) -> tuple[int, int]: ...

    def find_by_date_range(
        self, user_id: int, data_types: list[str], since: datetime, until: datetime
    ) -> list[Measurement]: ...

    def find_recent_entries(
        self, user_id: int, limit: int = 20
    ) -> list[Measurement]: ...

    def find_by_metric_type_paginated(
        self, metric_type_id: int, user_id: int, offset: int = 0, limit: int = 25
    ) -> tuple[list[Measurement], int]: ...

    def count_by_metric_type(self, metric_type_id: int, user_id: int) -> int: ...

    def get_latest_by_metric_type(
        self, metric_type_id: int, user_id: int
    ) -> Measurement | None: ...


@runtime_checkable
class IMetricTypeRepository(IRepository[MetricType], Protocol):
    def find_all(self, user_id: int | None = None) -> list[MetricType]: ...

    def find_by_name(self, name: str) -> MetricType | None: ...

    def find_by_name_and_user(self, name: str, user_id: int) -> MetricType | None: ...

    def reorder(self, user_id: int, ordered_ids: list[int]) -> None: ...


@runtime_checkable
class IGoalRepository(IRepository[Goal], Protocol):
    def find_by_user(self, user_id: int) -> list[Goal]: ...

    def find_all_goals(self) -> list[Goal]: ...


@runtime_checkable
class IApiTokenRepository(IRepository[ApiToken], Protocol):
    def find_by_user(self, user_id: int) -> list[ApiToken]: ...

    def find_all_by_user(self, user_id: int) -> list[ApiToken]: ...

    def find_by_prefix(self, token_prefix: str) -> list[ApiToken]: ...

    def list_all_active(self) -> list[ApiToken]: ...

    def record_usage(self, token: ApiToken) -> None: ...


@runtime_checkable
class ISystemConfigRepository(IRepository[SystemConfig], Protocol):
    def get_all(self) -> list[SystemConfig]: ...

    def get_by_key(self, key: str) -> SystemConfig | None: ...

    def upsert(self, key: str, value: str, **kwargs) -> SystemConfig: ...

    def seed_missing(self, defaults: list[SystemConfig]) -> int: ...


@runtime_checkable
class IDashboardWidgetRepository(IRepository[DashboardWidget], Protocol):
    def find_by_user(self, user_id: int) -> list[DashboardWidget]: ...

    def reorder(self, user_id: int, ordered_ids: list[int]) -> None: ...

    def find_by_user_and_metric(
        self, user_id: int, metric_type_id: int
    ) -> DashboardWidget | None: ...


@runtime_checkable
class IInsightRepository(IRepository[Insight], Protocol):
    def find_by_user_and_date(
        self, user_id: int, query_date: str
    ) -> Insight | None: ...

    def list_by_user(self, user_id: int, limit: int = 30) -> list[Insight]: ...


@runtime_checkable
class ISharingRepository(IRepository[SharingRelationship], Protocol):
    def find_by_owner(self, owner_id: int) -> list[SharingRelationship]: ...

    def find_by_grantee(self, grantee_handle: str) -> list[SharingRelationship]: ...

    def get_active_relationship(
        self, owner_id: int, grantee_handle: str, metric_type_id: int
    ) -> SharingRelationship | None: ...

    def find_pending_by_grantee(
        self, grantee_handle: str
    ) -> list[SharingRelationship]: ...

    def find_active_by_grantee(
        self, grantee_handle: str
    ) -> list[SharingRelationship]: ...

    def find_active_between(
        self, user_a_id: int, user_b_handle: str
    ) -> SharingRelationship | None: ...

    def find_pending_relationship(
        self, owner_id: int, grantee_handle: str, metric_type_id: int
    ) -> SharingRelationship | None: ...

    def find_active_for_remote_owner(
        self, owner_handle: str, data_type: str
    ) -> SharingRelationship | None: ...

    def find_pending_by_token_hash(
        self, token_hash: str
    ) -> SharingRelationship | None: ...

    def find_active_by_owner_id(
        self, owner_id: int
    ) -> list[SharingRelationship]: ...

    def find_active_by_owner_and_data_type(
        self, owner_id: int, data_type: str
    ) -> list[SharingRelationship]: ...

    def find_active_by_token_hash(
        self, token_hash: str
    ) -> SharingRelationship | None: ...

    def find_active_with_owner_metric_and_grantee(
        self, owner_id: int, grantee_handle: str, metric_type_id: int
    ) -> SharingRelationship | None: ...


@runtime_checkable
class IExerciseRepository(IRepository[Exercise], Protocol):
    def find_all_catalog(self, user_id: int) -> list[Exercise]: ...

    def find_by_name(self, name: str) -> Exercise | None: ...


@runtime_checkable
class IWorkoutPlanRepository(IRepository[WorkoutPlan], Protocol):
    def find_by_user(self, user_id: int) -> list[WorkoutPlan]: ...

    def reorder(self, user_id: int, ordered_ids: list[int]) -> None: ...


@runtime_checkable
class IWorkoutSessionRepository(IRepository[WorkoutSession], Protocol):
    def find_recent_by_user(
        self, user_id: int, limit: int = 10
    ) -> list[WorkoutSession]: ...

    def get_last_session_for_plan(
        self, user_id: int, plan_id: int
    ) -> WorkoutSession | None: ...

    def get_personal_records(
        self, user_id: int, exercise_ids: list[int]
    ) -> dict[int, dict]: ...

    def find_all_by_user(self, user_id: int) -> list[WorkoutSession]: ...

    def count_completed_in_range(
        self, user_id: int, since: "datetime", until: "datetime"
    ) -> int: ...

    def find_completed_in_range(
        self, user_id: int, since: "datetime", until: "datetime"
    ) -> list[WorkoutSession]: ...

    def find_active_by_user(self, user_id: int) -> WorkoutSession | None: ...

    def get_by_id_with_relations(
        self, session_id: int, user_id: int
    ) -> WorkoutSession | None: ...

    def find_completed_by_plan(
        self, user_id: int, plan_id: int
    ) -> list[WorkoutSession]: ...


@runtime_checkable
class IWorkoutPlanExerciseRepository(IRepository[WorkoutPlanExercise], Protocol):
    def find_by_plan(self, plan_id: int) -> list[WorkoutPlanExercise]: ...

    def replace_exercises_for_plan(
        self, plan_id: int, exercises: list[WorkoutPlanExercise]
    ) -> None: ...


@runtime_checkable
class IWorkoutLogEntryRepository(IRepository[WorkoutLogEntry], Protocol):
    def find_by_session_exercise_set(
        self, session_id: int, exercise_id: int, set_number: int
    ) -> WorkoutLogEntry | None: ...

    def find_exercise_history(
        self, user_id: int, exercise_id: int
    ) -> list[WorkoutLogEntry]: ...


@runtime_checkable
class IShareRecipientRepository(IRepository[ShareRecipient], Protocol):
    def find_by_user(self, user_id: int) -> list[ShareRecipient]: ...


@runtime_checkable
class IAsymmetricShareRepository(IRepository[AsymmetricShare], Protocol):
    def find_by_user(self, user_id: int) -> list[AsymmetricShare]: ...

    def get_by_id_secure(self, share_id: int) -> AsymmetricShare | None: ...


@runtime_checkable
class ICircadianProfileRepository(IRepository[CircadianProfile], Protocol):
    def find_by_user(self, user_id: int) -> CircadianProfile | None: ...


@runtime_checkable
class ILeaderboardGroupRepository(IRepository[LeaderboardGroup], Protocol):
    def find_by_creator(self, creator_id: int) -> list[LeaderboardGroup]: ...

    def find_by_invite_code(self, code: str) -> LeaderboardGroup | None: ...

    def find_joined_by_user(self, user_handle: str) -> list[LeaderboardGroup]: ...


@runtime_checkable
class ILeaderboardMemberRepository(IRepository[LeaderboardMember], Protocol):
    def find_by_group_id(self, group_id: int) -> list[LeaderboardMember]: ...

    def get_member(
        self, group_id: int, user_handle: str
    ) -> LeaderboardMember | None: ...


@runtime_checkable
class INotificationRepository(IRepository[Notification], Protocol):
    def find_by_user(self, user_id: int, limit: int = 20) -> list[Notification]: ...

    def find_unread_by_user(self, user_id: int) -> list[Notification]: ...

    def mark_all_read(self, user_id: int) -> None: ...


@runtime_checkable
class ISyncPushLogRepository(IRepository[SyncPushLog], Protocol):
    def cleanup_expired(self, ttl_hours: int = 24) -> int: ...

    def find_by_client_ids(self, client_ids: list[str]) -> list[SyncPushLog]: ...


@runtime_checkable
class IFederatedMeasurementCacheRepository(IRepository[FederatedMeasurementCache], Protocol):
    def get_cache(
        self, owner_handle: str, data_type: str, date_str: str, max_age_seconds: int = 60
    ) -> FederatedMeasurementCache | None: ...

    def upsert_cache(
        self, owner_handle: str, data_type: str, date_str: str,
        value_numeric: float | None, value_json: str | None,
    ) -> FederatedMeasurementCache: ...


@runtime_checkable
class IFederatedAccessLogRepository(IRepository[FederatedAccessLog], Protocol):
    def find_by_owner(self, owner_id: int) -> list[FederatedAccessLog]: ...
