from typing import Protocol

from sqlmodel import Session

from salus.repositories.api_token import ApiTokenRepository
from salus.repositories.dashboard import DashboardWidgetRepository
from salus.repositories.goal import GoalRepository
from salus.repositories.insight import InsightRepository
from salus.repositories.measurement import MeasurementRepository
from salus.repositories.metric_type import MetricTypeRepository
from salus.repositories.protocols import (
    IApiTokenRepository,
    IDashboardWidgetRepository,
    IGoalRepository,
    IInsightRepository,
    IMeasurementRepository,
    IMetricTypeRepository,
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


class IUnitOfWork(Protocol):
    session: Session
    users: IUserRepository
    identities: IUserIdentityRepository
    metric_types: IMetricTypeRepository
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

    def __enter__(self) -> "IUnitOfWork": ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class SqlUnitOfWork:
    users: IUserRepository
    identities: IUserIdentityRepository
    metric_types: IMetricTypeRepository
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

    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.identities = UserIdentityRepository(session)
        self.metric_types = MetricTypeRepository(session)
        self.measurements = MeasurementRepository(session)
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
