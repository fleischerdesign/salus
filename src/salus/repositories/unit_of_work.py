from typing import Protocol, TYPE_CHECKING

from sqlmodel import Session

from salus.repositories.api_token import ApiTokenRepository
from salus.repositories.dashboard import DashboardWidgetRepository
from salus.repositories.goal import GoalRepository
from salus.repositories.insight import InsightRepository
from salus.repositories.measurement import MeasurementRepository
from salus.repositories.metric_definition import MetricDefinitionRepository
from salus.repositories.metric_group import MetricGroupRepository
from salus.repositories.metric_preference import MetricPreferenceRepository
from salus.repositories.protocols import (
    IApiTokenRepository,
    IDashboardWidgetRepository,
    IGoalRepository,
    IInsightRepository,
    IMeasurementRepository,
    IMetricDefinitionRepository,
    IMetricGroupRepository,
    IMetricPreferenceRepository,
    ISystemConfigRepository,
    IUserIdentityRepository,
    IUserRepository,
    ISharingRepository,
    IExerciseRepository,
    IWorkoutPlanRepository,
    IWorkoutSessionRepository,
    IShareRecipientRepository,
    IAsymmetricShareRepository,
    ICircadianProfileRepository,
    ILeaderboardGroupRepository,
    ILeaderboardMemberRepository,
    INotificationRepository,
    ISyncPushLogRepository,
    IFederatedMeasurementCacheRepository,
    IFederatedAccessLogRepository,
    IWorkoutPlanExerciseRepository,
    IWorkoutLogEntryRepository,
    IHabitRepository,
    IHabitLogRepository,
    IMoodTagRepository,
    IMoodEntryRepository,
    IJournalEntryRepository,
    IAchievementDefinitionRepository,
    IUserAchievementRepository,
    IMedicationRepository,
    IMedicationScheduleRepository,
    IMedicationLogRepository,
    IMedicationInventoryRepository,
)
from salus.repositories.system_config import SystemConfigRepository
from salus.repositories.user import UserRepository
from salus.repositories.user_identity import UserIdentityRepository
from salus.repositories.sharing import SharingRepository
from salus.repositories.workout import (
    ExerciseRepository,
    WorkoutPlanRepository,
    WorkoutSessionRepository,
)
from salus.repositories.asymmetric_share import (
    ShareRecipientRepository,
    AsymmetricShareRepository,
)
from salus.repositories.circadian import CircadianProfileRepository
from salus.repositories.leaderboard import (
    LeaderboardGroupRepository,
    LeaderboardMemberRepository,
)
from salus.repositories.notification import NotificationRepository
from salus.repositories.sync_push_log import SyncPushLogRepository
from salus.repositories.federated_measurement_cache import FederatedMeasurementCacheRepository
from salus.repositories.federated_access_log import FederatedAccessLogRepository
from salus.repositories.workout_plan_exercise import WorkoutPlanExerciseRepository
from salus.repositories.workout_log_entry import WorkoutLogEntryRepository
from salus.repositories.habit import HabitRepository, HabitLogRepository
from salus.repositories.mood import MoodTagRepository, MoodEntryRepository
from salus.repositories.journal import JournalEntryRepository
from salus.repositories.achievement import AchievementDefinitionRepository, UserAchievementRepository
from salus.repositories.medication import (
    MedicationRepository,
    MedicationScheduleRepository,
    MedicationLogRepository,
    MedicationInventoryRepository,
)

if TYPE_CHECKING:
    from salus.services.plugin.hooks import HookRegistry


class IUnitOfWork(Protocol):
    session: Session
    users: IUserRepository
    identities: IUserIdentityRepository
    metric_definitions: IMetricDefinitionRepository
    metric_groups: IMetricGroupRepository
    metric_preferences: IMetricPreferenceRepository
    measurements: IMeasurementRepository
    goals: IGoalRepository
    api_tokens: IApiTokenRepository
    system_configs: ISystemConfigRepository
    dashboard_widgets: IDashboardWidgetRepository
    insights: IInsightRepository
    sharing_relationships: ISharingRepository
    exercises: IExerciseRepository
    workout_plans: IWorkoutPlanRepository
    workout_sessions: IWorkoutSessionRepository
    share_recipients: IShareRecipientRepository
    asymmetric_shares: IAsymmetricShareRepository
    circadian_profiles: ICircadianProfileRepository
    leaderboard_groups: ILeaderboardGroupRepository
    leaderboard_members: ILeaderboardMemberRepository
    notifications: INotificationRepository
    sync_push_logs: ISyncPushLogRepository
    federated_measurement_cache: IFederatedMeasurementCacheRepository
    federated_access_logs: IFederatedAccessLogRepository
    workout_plan_exercises: IWorkoutPlanExerciseRepository
    workout_log_entries: IWorkoutLogEntryRepository

    habits: IHabitRepository
    habit_logs: IHabitLogRepository
    mood_tags: IMoodTagRepository
    mood_entries: IMoodEntryRepository
    journal_entries: IJournalEntryRepository
    achievement_definitions: IAchievementDefinitionRepository
    user_achievements: IUserAchievementRepository

    medications: IMedicationRepository
    medication_schedules: IMedicationScheduleRepository
    medication_logs: IMedicationLogRepository
    medication_inventories: IMedicationInventoryRepository

    def __enter__(self) -> "IUnitOfWork": ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class SqlUnitOfWork:
    users: IUserRepository
    identities: IUserIdentityRepository
    metric_definitions: IMetricDefinitionRepository
    metric_groups: IMetricGroupRepository
    metric_preferences: IMetricPreferenceRepository
    measurements: IMeasurementRepository
    goals: IGoalRepository
    api_tokens: IApiTokenRepository
    system_configs: ISystemConfigRepository
    dashboard_widgets: IDashboardWidgetRepository
    insights: IInsightRepository
    sharing_relationships: ISharingRepository
    exercises: IExerciseRepository
    workout_plans: IWorkoutPlanRepository
    workout_sessions: IWorkoutSessionRepository
    share_recipients: IShareRecipientRepository
    asymmetric_shares: IAsymmetricShareRepository
    circadian_profiles: ICircadianProfileRepository
    leaderboard_groups: ILeaderboardGroupRepository
    leaderboard_members: ILeaderboardMemberRepository
    notifications: INotificationRepository
    sync_push_logs: ISyncPushLogRepository
    federated_measurement_cache: IFederatedMeasurementCacheRepository
    federated_access_logs: IFederatedAccessLogRepository
    workout_plan_exercises: IWorkoutPlanExerciseRepository
    workout_log_entries: IWorkoutLogEntryRepository
    habits: IHabitRepository
    habit_logs: IHabitLogRepository
    mood_tags: IMoodTagRepository
    mood_entries: IMoodEntryRepository
    journal_entries: IJournalEntryRepository
    achievement_definitions: IAchievementDefinitionRepository
    user_achievements: IUserAchievementRepository
    medications: IMedicationRepository
    medication_schedules: IMedicationScheduleRepository
    medication_logs: IMedicationLogRepository
    medication_inventories: IMedicationInventoryRepository

    def __init__(self, session: Session, registry: "HookRegistry | None" = None) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.identities = UserIdentityRepository(session)
        self.metric_definitions = MetricDefinitionRepository(session)
        self.metric_groups = MetricGroupRepository(session)
        self.metric_preferences = MetricPreferenceRepository(session)
        self.measurements = MeasurementRepository(session, registry=registry)
        self.goals = GoalRepository(session)
        self.api_tokens = ApiTokenRepository(session)
        self.system_configs = SystemConfigRepository(session)
        self.dashboard_widgets = DashboardWidgetRepository(session)
        self.insights = InsightRepository(session)
        self.sharing_relationships = SharingRepository(session)
        self.exercises = ExerciseRepository(session)
        self.workout_plans = WorkoutPlanRepository(session)
        self.workout_sessions = WorkoutSessionRepository(session)
        self.share_recipients = ShareRecipientRepository(session)
        self.asymmetric_shares = AsymmetricShareRepository(session)
        self.circadian_profiles = CircadianProfileRepository(session)
        self.leaderboard_groups = LeaderboardGroupRepository(session)
        self.leaderboard_members = LeaderboardMemberRepository(session)
        self.notifications = NotificationRepository(session)
        self.sync_push_logs = SyncPushLogRepository(session)
        self.federated_measurement_cache = FederatedMeasurementCacheRepository(session)
        self.federated_access_logs = FederatedAccessLogRepository(session)
        self.workout_plan_exercises = WorkoutPlanExerciseRepository(session)
        self.workout_log_entries = WorkoutLogEntryRepository(session)
        self.habits = HabitRepository(session)
        self.habit_logs = HabitLogRepository(session)
        self.mood_tags = MoodTagRepository(session)
        self.mood_entries = MoodEntryRepository(session)
        self.journal_entries = JournalEntryRepository(session)
        self.achievement_definitions = AchievementDefinitionRepository(session)
        self.user_achievements = UserAchievementRepository(session)
        self.medications = MedicationRepository(session)
        self.medication_schedules = MedicationScheduleRepository(session)
        self.medication_logs = MedicationLogRepository(session)
        self.medication_inventories = MedicationInventoryRepository(session)

    def __enter__(self) -> "SqlUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
