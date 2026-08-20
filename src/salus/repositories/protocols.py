from datetime import date, datetime, tzinfo
from typing import Protocol, TypeVar, runtime_checkable

from sqlmodel import Session

from salus.services.constants import DEDUP_TTL_HOURS
from salus.models.api_token import ApiToken
from salus.models.dashboard import DashboardWidget
from salus.models.goal import Goal
from salus.models.insight import Insight
from salus.models.measurement import Measurement
from salus.models.metric_definition import MetricDefinition, MetricGroup
from salus.models.metric_preference import UserMetricPreference
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
from salus.models.workout import Exercise, Program, ProgramWorkout, Workout, WorkoutSession, WorkoutExercise, WorkoutSet
from salus.models.asymmetric_share import ShareRecipient, AsymmetricShare
from salus.models.circadian import CircadianProfile
from salus.models.notification import Notification
from salus.models.sync_push_log import SyncPushLog
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

T = TypeVar("T")


@runtime_checkable
class IRepository(Protocol[T]):
    session: Session

    def get_by_id(self, id: str) -> T | None: ...

    def create(self, obj: T, auto_commit: bool = True) -> T: ...

    def update(self, obj: T, auto_commit: bool = True) -> T: ...

    def delete(self, obj: T, auto_commit: bool = True) -> None: ...

    def add(self, obj: T) -> None: ...

    def add_all(self, objs: list[T]) -> None: ...

    def commit(self) -> None: ...


@runtime_checkable
class IUserRepository(IRepository[User], Protocol):
    def get_by_username(self, username: str) -> User | None: ...

    def get_by_email(self, email: str) -> User | None: ...

    def find_first_admin(self) -> User | None: ...

    def list_all(self) -> list[User]: ...

    def toggle_admin(self, user_id: str) -> User: ...

    def toggle_active(self, user_id: str) -> User: ...


@runtime_checkable
class IUserIdentityRepository(IRepository[UserIdentity], Protocol):
    def get_by_provider_user_id(
        self, provider: str, provider_user_id: str
    ) -> UserIdentity | None: ...

    def list_by_user(self, user_id: str) -> list[UserIdentity]: ...


@runtime_checkable
class IMeasurementRepository(IRepository[Measurement], Protocol):
    def find_start_dates(self, user_id: str, tz: tzinfo | None = None) -> list[date]: ...

    def find_by_metric_type(
        self, metric_code: str, user_id: str | None = None
    ) -> list[Measurement]: ...

    def find_all(
        self,
        user_id: str | None = None,
        source_data_types: list[str] | None = None,
        sources: list[str] | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
    ) -> list[Measurement]: ...

    def find_latest(
        self, source_data_type: str, user_id: str | None = None
    ) -> Measurement | None: ...

    def upsert_all(self, records: list[Measurement]) -> tuple[int, int, list[Measurement]]: ...

    def find_by_date_range(
        self, user_id: str, source_data_types: list[str], since: datetime, until: datetime
    ) -> list[Measurement]: ...

    def find_recent_entries(
        self, user_id: str, limit: int = 20
    ) -> list[Measurement]: ...

    def find_by_external_id(
        self, external_id: str, source: str | None = None
    ) -> Measurement | None: ...

    def get_latest_by_metric_type(
        self, metric_code: str, user_id: str
    ) -> Measurement | None: ...


@runtime_checkable
class IMetricDefinitionRepository(IRepository[MetricDefinition], Protocol):
    def find_all(self) -> list[MetricDefinition]: ...

    def find_by_code(self, code: str) -> MetricDefinition | None: ...

    def find_by_source_data_type(self, source_data_type: str) -> MetricDefinition | None: ...

    def find_by_group(self, group_key: str) -> list[MetricDefinition]: ...


@runtime_checkable
class IMetricGroupRepository(IRepository[MetricGroup], Protocol):
    def find_all(self) -> list[MetricGroup]: ...

    def find_by_key(self, key: str) -> MetricGroup | None: ...


@runtime_checkable
class IMetricPreferenceRepository(IRepository[UserMetricPreference], Protocol):
    def find_all(self, user_id: str) -> list[UserMetricPreference]: ...

    def find_by_user_and_code(self, user_id: str, metric_code: str) -> UserMetricPreference | None: ...

    def reorder(self, user_id: str, ordered_codes: list[str]) -> None: ...


@runtime_checkable
class IGoalRepository(IRepository[Goal], Protocol):
    def find_by_user(self, user_id: str) -> list[Goal]: ...

    def find_all_goals(self) -> list[Goal]: ...


@runtime_checkable
class IApiTokenRepository(IRepository[ApiToken], Protocol):
    def find_by_user(self, user_id: str) -> list[ApiToken]: ...

    def find_all_by_user(self, user_id: str) -> list[ApiToken]: ...

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
    def find_by_user(self, user_id: str) -> list[DashboardWidget]: ...

    def reorder(self, user_id: str, ordered_ids: list[str]) -> None: ...

    def find_by_user_and_metric(
        self, user_id: str, metric_code: str
    ) -> DashboardWidget | None: ...


@runtime_checkable
class IInsightRepository(IRepository[Insight], Protocol):
    def find_by_user_and_date(
        self, user_id: str, query_date: str
    ) -> Insight | None: ...

    def list_by_user(self, user_id: str, limit: int = 30) -> list[Insight]: ...


@runtime_checkable
class ISharingRepository(IRepository[SharingRelationship], Protocol):
    def find_by_owner(self, owner_id: str) -> list[SharingRelationship]: ...

    def find_by_grantee(self, grantee_handle: str) -> list[SharingRelationship]: ...

    def get_active_relationship(
        self, owner_id: str, grantee_handle: str, metric_code: str
    ) -> SharingRelationship | None: ...

    def find_pending_by_grantee(
        self, grantee_handle: str
    ) -> list[SharingRelationship]: ...

    def find_active_by_grantee(
        self, grantee_handle: str
    ) -> list[SharingRelationship]: ...

    def find_active_between(
        self, user_a_id: str, user_b_handle: str
    ) -> SharingRelationship | None: ...

    def find_pending_relationship(
        self, owner_id: str, grantee_handle: str, metric_code: str
    ) -> SharingRelationship | None: ...

    def find_active_for_remote_owner(
        self, owner_handle: str, source_data_type: str
    ) -> SharingRelationship | None: ...

    def find_pending_by_token_hash(
        self, token_hash: str
    ) -> SharingRelationship | None: ...

    def find_active_by_owner_id(
        self, owner_id: str
    ) -> list[SharingRelationship]: ...

    def find_active_by_owner_and_data_type(
        self, owner_id: str, source_data_type: str
    ) -> list[SharingRelationship]: ...

    def find_active_by_token_hash(
        self, token_hash: str
    ) -> SharingRelationship | None: ...

    def find_active_with_owner_metric_and_grantee(
        self, owner_id: str, grantee_handle: str, metric_code: str
    ) -> SharingRelationship | None: ...


@runtime_checkable
class IExerciseRepository(IRepository[Exercise], Protocol):
    def find_all_catalog(self, user_id: str) -> list[Exercise]: ...

    def find_by_name(self, name: str) -> Exercise | None: ...


@runtime_checkable
class IWorkoutRepository(IRepository[Workout], Protocol):
    def find_by_user(self, user_id: str) -> list[Workout]: ...

    def reorder(self, user_id: str, ordered_ids: list[str]) -> None: ...


@runtime_checkable
class IProgramRepository(IRepository[Program], Protocol):
    def find_by_user(self, user_id: str) -> list[Program]: ...

    def reorder(self, user_id: str, ordered_ids: list[str]) -> None: ...


@runtime_checkable
class IProgramWorkoutRepository(IRepository[ProgramWorkout], Protocol):
    def find_by_program(self, program_id: str) -> list[ProgramWorkout]: ...

    def replace_workouts_for_program(
        self, program_id: str, slots: list[ProgramWorkout]
    ) -> None: ...


@runtime_checkable
class IWorkoutSessionRepository(IRepository[WorkoutSession], Protocol):
    def find_recent_by_user(
        self, user_id: str, limit: int = 10
    ) -> list[WorkoutSession]: ...

    def get_last_session_for_workout(
        self, user_id: str, workout_id: str
    ) -> WorkoutSession | None: ...

    def get_personal_records(
        self, user_id: str, exercise_ids: list[str]
    ) -> dict[str, dict]: ...

    def find_all_by_user(self, user_id: str) -> list[WorkoutSession]: ...

    def find_completed_dates(self, user_id: str, tz: tzinfo | None = None) -> list[date]: ...

    def count_completed_in_range(
        self, user_id: str, since: "datetime", until: "datetime"
    ) -> int: ...

    def find_completed_in_range(
        self, user_id: str, since: "datetime", until: "datetime"
    ) -> list[WorkoutSession]: ...

    def find_active_by_user(self, user_id: str) -> WorkoutSession | None: ...

    def get_by_id_with_relations(
        self, session_id: str, user_id: str
    ) -> WorkoutSession | None: ...

    def find_completed_by_workout(
        self, user_id: str, workout_id: str
    ) -> list[WorkoutSession]: ...


@runtime_checkable
class IWorkoutExerciseRepository(IRepository[WorkoutExercise], Protocol):
    def find_by_workout(self, workout_id: str) -> list[WorkoutExercise]: ...

    def replace_exercises_for_workout(
        self, workout_id: str, exercises: list[WorkoutExercise]
    ) -> None: ...


@runtime_checkable
class IWorkoutSetRepository(IRepository[WorkoutSet], Protocol):
    def find_by_session_exercise_set(
        self, session_id: str, exercise_id: str, set_number: int
    ) -> WorkoutSet | None: ...

    def find_exercise_history(
        self, user_id: str, exercise_id: str
    ) -> list[WorkoutSet]: ...

    def get_exercise_progression(
        self,
        user_id: str,
        exercise_id: str,
        since: "datetime | None" = None,
    ) -> list[dict]: ...


@runtime_checkable
class IShareRecipientRepository(IRepository[ShareRecipient], Protocol):
    def find_by_user(self, user_id: str) -> list[ShareRecipient]: ...


@runtime_checkable
class IAsymmetricShareRepository(IRepository[AsymmetricShare], Protocol):
    def find_by_user(self, user_id: str) -> list[AsymmetricShare]: ...

    def get_by_id_secure(self, share_id: str) -> AsymmetricShare | None: ...


@runtime_checkable
class ICircadianProfileRepository(IRepository[CircadianProfile], Protocol):
    def find_by_user(self, user_id: str) -> CircadianProfile | None: ...


@runtime_checkable
class ILeaderboardGroupRepository(IRepository[LeaderboardGroup], Protocol):
    def find_by_creator(self, creator_id: str) -> list[LeaderboardGroup]: ...

    def find_by_invite_code(self, code: str) -> LeaderboardGroup | None: ...

    def find_joined_by_user(self, user_handle: str) -> list[LeaderboardGroup]: ...


@runtime_checkable
class ILeaderboardMemberRepository(IRepository[LeaderboardMember], Protocol):
    def find_by_group_id(self, group_id: str) -> list[LeaderboardMember]: ...

    def get_member(
        self, group_id: str, user_handle: str
    ) -> LeaderboardMember | None: ...


@runtime_checkable
class INotificationRepository(IRepository[Notification], Protocol):
    def find_by_user(self, user_id: str, limit: int = 20) -> list[Notification]: ...

    def find_unread_by_user(self, user_id: str) -> list[Notification]: ...

    def mark_all_read(self, user_id: str) -> None: ...


@runtime_checkable
class ISyncPushLogRepository(IRepository[SyncPushLog], Protocol):
    def cleanup_expired(self, ttl_hours: int = DEDUP_TTL_HOURS) -> int: ...

    def find_by_client_ids(self, client_ids: list[str]) -> list[SyncPushLog]: ...


@runtime_checkable
class IFederatedMeasurementCacheRepository(IRepository[FederatedMeasurementCache], Protocol):
    def get_cache(
        self, owner_handle: str, source_data_type: str, date_str: str, max_age_seconds: int = 60
    ) -> FederatedMeasurementCache | None: ...

    def upsert_cache(
        self, owner_handle: str, source_data_type: str, date_str: str,
        value_numeric: float | None, value_json: str | None,
    ) -> FederatedMeasurementCache: ...


@runtime_checkable
class IFederatedAccessLogRepository(IRepository[FederatedAccessLog], Protocol):
    def find_by_owner(self, owner_id: str) -> list[FederatedAccessLog]: ...


@runtime_checkable
class IHabitRepository(IRepository[Habit], Protocol):
    def find_by_user(self, user_id: str) -> list[Habit]: ...

    def find_active(self, user_id: str) -> list[Habit]: ...


@runtime_checkable
class IHabitLogRepository(IRepository[HabitLog], Protocol):
    def find_by_habit(self, habit_id: str) -> list[HabitLog]: ...

    def find_by_habit_and_user(self, habit_id: str, user_id: str) -> list[HabitLog]: ...

    def find_by_user_and_date_range(self, user_id: str, since: date, until: date) -> list[HabitLog]: ...

    def find_by_habit_and_date(self, habit_id: str, log_date: date) -> HabitLog | None: ...

    def find_all_by_user(self, user_id: str) -> list[HabitLog]: ...

    def find_completed_dates_by_user(self, user_id: str) -> dict[str, list[date]]: ...


@runtime_checkable
class IMoodTagRepository(IRepository[MoodTag], Protocol):
    def find_all_tags(self) -> list[MoodTag]: ...


@runtime_checkable
class IMoodEntryRepository(IRepository[MoodEntry], Protocol):
    def find_dates(self, user_id: str) -> list[date]: ...

    def find_by_user(self, user_id: str) -> list[MoodEntry]: ...

    def find_by_user_range(self, user_id: str, since: date, until: date) -> list[MoodEntry]: ...

    def find_by_user_and_date(self, user_id: str, entry_date: date) -> MoodEntry | None: ...


@runtime_checkable
class IJournalEntryRepository(IRepository[JournalEntry], Protocol):
    def find_by_user(self, user_id: str, offset: int = 0, limit: int = 20) -> list[JournalEntry]: ...

    def count_by_user(self, user_id: str) -> int: ...

    def find_by_user_range(self, user_id: str, since: date, until: date) -> list[JournalEntry]: ...

    def find_by_user_and_date(self, user_id: str, entry_date: date) -> JournalEntry | None: ...

    def search(self, user_id: str, query: str, offset: int = 0, limit: int = 20) -> list[JournalEntry]: ...


@runtime_checkable
class IAchievementDefinitionRepository(IRepository[AchievementDefinition], Protocol):
    def find_all(self) -> list[AchievementDefinition]: ...

    def find_by_code(self, code: str) -> AchievementDefinition | None: ...

    def find_by_category(self, category: str) -> list[AchievementDefinition]: ...


@runtime_checkable
class IUserAchievementRepository(IRepository[UserAchievement], Protocol):
    def find_by_user(self, user_id: str) -> list[UserAchievement]: ...

    def find_by_user_and_code(self, user_id: str, achievement_code: str) -> UserAchievement | None: ...


@runtime_checkable
class IMedicationRepository(IRepository[Medication], Protocol):
    def find_by_user(self, user_id: str) -> list[Medication]: ...

    def find_active(self, user_id: str) -> list[Medication]: ...


@runtime_checkable
class IMedicationScheduleRepository(IRepository[MedicationSchedule], Protocol):
    def find_by_medication(self, medication_id: str) -> list[MedicationSchedule]: ...

    def find_by_user(self, user_id: str) -> list[MedicationSchedule]: ...


@runtime_checkable
class IMedicationLogRepository(IRepository[MedicationLog], Protocol):
    def find_by_medication(self, medication_id: str) -> list[MedicationLog]: ...

    def find_by_user_and_range(self, user_id: str, start: datetime, end: datetime) -> list[MedicationLog]: ...

    def find_by_schedule_and_time(self, schedule_id: str, taken_at_start: datetime, taken_at_end: datetime) -> MedicationLog | None: ...

    def find_all_by_user(self, user_id: str) -> list[MedicationLog]: ...


@runtime_checkable
class IMedicationInventoryRepository(IRepository[MedicationInventory], Protocol):
    def find_by_medication(self, medication_id: str) -> MedicationInventory | None: ...


@runtime_checkable
class IFoodItemRepository(IRepository[FoodItem], Protocol):
    def search(self, query: str, limit: int = 20) -> list[FoodItem]: ...

    def find_by_barcode(self, barcode: str) -> FoodItem | None: ...

    def find_all_verified(self) -> list[FoodItem]: ...

    def find_by_user(self, user_id: str) -> list[FoodItem]: ...

    def find_frequent(self, user_id: str, limit: int = 20) -> list[FoodItem]: ...


@runtime_checkable
class IMealRepository(IRepository[Meal], Protocol):
    def find_by_user_and_date_range(self, user_id: str, since: date, until: date) -> list[Meal]: ...

    def find_by_user_and_date(self, user_id: str, log_date: date) -> list[Meal]: ...

    def find_by_user(self, user_id: str) -> list[Meal]: ...


@runtime_checkable
class IMealItemRepository(IRepository[MealItem], Protocol):
    def find_by_meal(self, meal_id: str) -> list[MealItem]: ...


@runtime_checkable
class IRecipeRepository(IRepository[Recipe], Protocol):
    def find_by_user(self, user_id: str) -> list[Recipe]: ...


@runtime_checkable
class IRecipeIngredientRepository(IRepository[RecipeIngredient], Protocol):
    def find_by_recipe(self, recipe_id: str) -> list[RecipeIngredient]: ...


@runtime_checkable
class IUserSourcePreferenceRepository(IRepository[UserSourcePreference], Protocol):
    def find_by_user(self, user_id: str) -> list[UserSourcePreference]: ...

    def find_by_user_and_metric(self, user_id: str, metric_code: str) -> list[UserSourcePreference]: ...

    def find_by_user_metric_source(
        self, user_id: str, metric_code: str, source: str
    ) -> UserSourcePreference | None: ...


@runtime_checkable
class IUserSourceStatusRepository(IRepository[UserSourceStatus], Protocol):
    def find_by_user(self, user_id: str) -> list[UserSourceStatus]: ...

    def find_by_user_source(self, user_id: str, source: str) -> UserSourceStatus | None: ...


@runtime_checkable
class ILabMarkerRepository(IRepository[LabMarker], Protocol):
    def find_all(self) -> list[LabMarker]: ...

    def find_by_code(self, code: str) -> LabMarker | None: ...


@runtime_checkable
class ILabPanelRepository(IRepository[LabPanel], Protocol):
    def find_by_user(self, user_id: str) -> list[LabPanel]: ...

    def find_by_user_and_date_range(
        self, user_id: str, since: date, until: date
    ) -> list[LabPanel]: ...


@runtime_checkable
class ILabResultRepository(IRepository[LabResult], Protocol):
    def find_by_panel(self, panel_id: str) -> list[LabResult]: ...


@runtime_checkable
class IFastingSessionRepository(IRepository[FastingSession], Protocol):
    def find_active_by_user(self, user_id: str) -> FastingSession | None: ...

    def find_by_user(self, user_id: str) -> list[FastingSession]: ...


@runtime_checkable
class IFastingProtocolRepository(IRepository[FastingProtocol], Protocol):
    def find_by_user(self, user_id: str) -> list[FastingProtocol]: ...


@runtime_checkable
class IDataQualityFlagRepository(IRepository[DataQualityFlag], Protocol):
    def find_by_user(self, user_id: str, limit: int = 100) -> list[DataQualityFlag]: ...

    def find_by_measurement(self, measurement_id: str) -> list[DataQualityFlag]: ...
