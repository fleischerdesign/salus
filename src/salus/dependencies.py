from collections.abc import Generator

from fastapi import Depends, Header, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session

from salus.config import settings
from salus.database import get_session
from salus.exceptions import AuthenticationError, ForbiddenError
from salus.models.user import User
from salus.repositories.api_token import ApiTokenRepository
from salus.repositories.dashboard import DashboardWidgetRepository
from salus.repositories.measurement import MeasurementRepository
from salus.repositories.metric_definition import MetricDefinitionRepository
from salus.repositories.system_config import SystemConfigRepository
from salus.repositories.unit_of_work import IUnitOfWork, SqlUnitOfWork
from salus.repositories.user import UserRepository
from salus.repositories.user_identity import UserIdentityRepository
from salus.services.plugin.hooks import HookRegistry
from salus.services.plugin.manager import PluginManager
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.orchestrator import AnalyticsService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.weight import WeightAnalysisService
from salus.services.analytics.blood_pressure import BloodPressureAnalysisService
from salus.services.admin import AdminService
from salus.services.config import ConfigService
from salus.services.api_token import ApiTokenService
from salus.services.auth.providers import (
    LdapAuthProvider,
    LocalAuthProvider,
    OidcAuthProvider,
)
from salus.services.auth.service import AuthService
from salus.services.dashboard_widget import DashboardWidgetService
from salus.services.export import ExportService
from salus.services.goal import GoalService
from salus.services.jwt import JwtService
from salus.services.measurement import MeasurementService
from salus.services.metric_definition import MetricDefinitionService
from salus.services.metric_group import MetricGroupService
from salus.services.metric_type_mapping import MetricDefinitionMappingService
from salus.services.parser import FlexiblePayloadParser
from salus.services.user import UserService
from salus.services.webhook_ingestion import WebhookIngestionService
from salus.repositories.insight import InsightRepository
from salus.services.sharing import (
    SharingService,
    RelationshipService,
    FederationKeyService,
    FederationDiscoveryService,
    FederationDataResolver,
    PeerNotificationService,
)
from salus.services.leaderboard import LeaderboardService
from salus.services.notification import NotificationService
from salus.repositories.protocols import IInsightRepository
from salus.services.insight.factory import LLMProviderFactory
from salus.services.insight.service import InsightService
from salus.services.workout.autoregulation import AutoregulationService
from salus.services.workout.planner import WorkoutService
from salus.services.backup.providers import IBackupStorageProvider
from salus.services.backup.service import BackupService
from salus.services.asymmetric_share import AsymmetricShareService
from salus.services.portability import DataPortabilityService
from salus.services.open_science import OpenScienceService
from salus.services.circadian import CircadianService
from salus.services.event_bus import EventBus
from salus.services.habit import HabitService
from salus.services.mood import MoodService
from salus.services.journal import JournalService
from salus.services.achievement.service import AchievementService


limiter = Limiter(key_func=get_remote_address)


def get_plugin_manager(request: Request) -> PluginManager | None:
    return getattr(request.app.state, "plugin_manager", None)


def get_plugin_registry(request: Request) -> HookRegistry | None:
    manager = get_plugin_manager(request)
    return manager.registry if manager else None


def get_unit_of_work(
    session: Session = Depends(get_session),
    registry: HookRegistry | None = Depends(get_plugin_registry),
) -> Generator[IUnitOfWork, None, None]:
    uow = SqlUnitOfWork(session, registry=registry)
    try:
        yield uow
    except Exception:
        uow.rollback()
        raise
    else:
        uow.commit()


def get_user_repo(session: Session = Depends(get_session)) -> UserRepository:
    return UserRepository(session)


def get_api_token_repo(session: Session = Depends(get_session)) -> ApiTokenRepository:
    return ApiTokenRepository(session)


def get_api_token_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> ApiTokenService:
    return ApiTokenService(uow)


async def verify_webhook_token(
    x_api_token: str | None = Header(None, alias="X-API-Token"),
    authorization: str | None = Header(None),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
    token: str | None = None

    if x_api_token:
        token = x_api_token
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()

    if token is None:
        raise HTTPException(status_code=401, detail="Missing webhook token")

    result = api_token_svc.resolve(token)
    if result is not None:
        user, api_token = result
        if not api_token.has_scope("ingest:write"):
            raise HTTPException(
                status_code=403, detail="Token lacks ingest:write scope"
            )
        return user

    if token == settings.api_token:
        admin = user_repo.find_first_admin()
        if admin is not None:
            return admin
        raise HTTPException(status_code=401, detail="No admin user configured")

    raise HTTPException(status_code=401, detail="Invalid webhook token")


TOKEN_COOKIE_NAME = "salus_session"


def _extract_token_from_request(request: Request) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header[7:].strip()
    return request.cookies.get(TOKEN_COOKIE_NAME)


def get_jwt_service() -> JwtService:
    return JwtService(
        secret=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expire_minutes=settings.jwt_expire_minutes,
    )


def get_user_identity_repo(
    session: Session = Depends(get_session),
) -> UserIdentityRepository:
    return UserIdentityRepository(session)


def get_metric_definition_repo(
    session: Session = Depends(get_session),
) -> MetricDefinitionRepository:
    return MetricDefinitionRepository(session)


def get_measurement_repo(
    session: Session = Depends(get_session),
    registry: HookRegistry | None = Depends(get_plugin_registry),
) -> MeasurementRepository:
    return MeasurementRepository(session, registry=registry)


def get_user_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> UserService:
    return UserService(uow)


def _build_oidc_providers(user_svc: UserService) -> dict[str, OidcAuthProvider]:
    providers: dict[str, OidcAuthProvider] = {}

    if settings.google_client_id and settings.google_client_secret:
        providers["google"] = OidcAuthProvider(
            name="google",
            issuer_url="https://accounts.google.com",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            user_service=user_svc,
        )

    if settings.github_client_id and settings.github_client_secret:
        providers["github"] = OidcAuthProvider(
            name="github",
            issuer_url="https://github.com/login/oauth",
            client_id=settings.github_client_id,
            client_secret=settings.github_client_secret,
            user_service=user_svc,
        )

    if (
        settings.oidc_issuer_url
        and settings.oidc_client_id
        and settings.oidc_client_secret
    ):
        providers["oidc"] = OidcAuthProvider(
            name="oidc",
            issuer_url=settings.oidc_issuer_url,
            client_id=settings.oidc_client_id,
            client_secret=settings.oidc_client_secret,
            user_service=user_svc,
        )

    return providers


def get_auth_service(
    jwt_svc: JwtService = Depends(get_jwt_service),
    user_svc: UserService = Depends(get_user_service),
) -> AuthService:
    ldap_provider: LdapAuthProvider | None = None
    if settings.ldap_server_uri and settings.ldap_base_dn:
        ldap_provider = LdapAuthProvider(
            user_service=user_svc,
            server_uri=settings.ldap_server_uri,
            base_dn=settings.ldap_base_dn,
            user_dn_template=settings.ldap_user_dn_template,
            use_tls=settings.ldap_use_tls,
        )
    return AuthService(
        jwt_svc=jwt_svc,
        user_svc=user_svc,
        local_provider=LocalAuthProvider(user_svc),
        ldap_provider=ldap_provider,
        oidc_providers=_build_oidc_providers(user_svc),
    )


def get_metric_definition_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> MetricDefinitionService:
    return MetricDefinitionService(uow)


def get_metric_group_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> MetricGroupService:
    return MetricGroupService(uow)


def get_measurement_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    registry: HookRegistry | None = Depends(get_plugin_registry),
) -> MeasurementService:
    return MeasurementService(uow, registry=registry)


def get_metric_definition_mapping_service(
    repo: MetricDefinitionRepository = Depends(get_metric_definition_repo),
) -> MetricDefinitionMappingService:
    return MetricDefinitionMappingService(repo)


def get_webhook_ingestion_service(
    measurement_repo: MeasurementRepository = Depends(get_measurement_repo),
    mapping_service: MetricDefinitionMappingService = Depends(
        get_metric_definition_mapping_service
    ),
    registry: HookRegistry | None = Depends(get_plugin_registry),
) -> WebhookIngestionService:
    parser = FlexiblePayloadParser()
    return WebhookIngestionService(
        parser, measurement_repo, mapping_service, registry=registry
    )


def get_goal_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    registry: HookRegistry | None = Depends(get_plugin_registry),
) -> GoalService:
    return GoalService(uow, registry=registry)


def get_export_service(
    repo: MeasurementRepository = Depends(get_measurement_repo),
) -> ExportService:
    return ExportService(repo)


def get_sleep_analysis_service(
    repo: MeasurementRepository = Depends(get_measurement_repo),
) -> SleepAnalysisService:
    return SleepAnalysisService(repo)


def get_activity_analysis_service(
    repo: MeasurementRepository = Depends(get_measurement_repo),
) -> ActivityAnalysisService:
    return ActivityAnalysisService(repo)


def get_weight_analysis_service(
    repo: MeasurementRepository = Depends(get_measurement_repo),
) -> WeightAnalysisService:
    return WeightAnalysisService(repo)


def get_nutrition_analysis_service(
    repo: MeasurementRepository = Depends(get_measurement_repo),
) -> NutritionAnalysisService:
    return NutritionAnalysisService(repo)


def get_blood_pressure_analysis_service(
    repo: MeasurementRepository = Depends(get_measurement_repo),
) -> BloodPressureAnalysisService:
    return BloodPressureAnalysisService(repo)


def get_analytics_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    sleep_svc: SleepAnalysisService = Depends(get_sleep_analysis_service),
    activity_svc: ActivityAnalysisService = Depends(get_activity_analysis_service),
    weight_svc: WeightAnalysisService = Depends(get_weight_analysis_service),
    nutrition_svc: NutritionAnalysisService = Depends(get_nutrition_analysis_service),
) -> AnalyticsService:
    return AnalyticsService(uow, sleep_svc, activity_svc, weight_svc, nutrition_svc)


def get_dashboard_widget_repo(
    session: Session = Depends(get_session),
) -> DashboardWidgetRepository:
    return DashboardWidgetRepository(session)


def get_dashboard_widget_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    activity_svc: ActivityAnalysisService = Depends(get_activity_analysis_service),
    sleep_svc: SleepAnalysisService = Depends(get_sleep_analysis_service),
    nutrition_svc: NutritionAnalysisService = Depends(get_nutrition_analysis_service),
    weight_svc: WeightAnalysisService = Depends(get_weight_analysis_service),
    goal_svc: GoalService = Depends(get_goal_service),
    bp_svc: BloodPressureAnalysisService = Depends(get_blood_pressure_analysis_service),
) -> DashboardWidgetService:
    return DashboardWidgetService(
        uow,
        activity_svc,
        sleep_svc,
        nutrition_svc,
        weight_svc,
        goal_svc,
        bp_svc,
    )


def get_current_user(
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
) -> User:
    token = _extract_token_from_request(request)
    if token is None:
        raise AuthenticationError("Not authenticated")

    user = auth_svc.get_user_from_token(token)
    if user is None:
        raise AuthenticationError("Invalid or expired token")
    return user


def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise ForbiddenError("Admin access required")
    return current_user


def get_admin_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AdminService:
    return AdminService(uow)


def get_system_config_repo(
    session: Session = Depends(get_session),
) -> SystemConfigRepository:
    return SystemConfigRepository(session)


def get_config_service(
    repo: SystemConfigRepository = Depends(get_system_config_repo),
) -> ConfigService:
    return ConfigService(repo)


def get_current_user_optional(
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
) -> User | None:
    token = _extract_token_from_request(request)
    if token is None:
        return None
    return auth_svc.get_user_from_token(token)


async def get_current_user_or_api(
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    authorization: str | None = Header(None),
    user_repo: UserRepository = Depends(get_user_repo),
) -> User:
    token: str | None = None

    if x_api_key:
        token = x_api_key
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()

    if token:
        if token == settings.api_token:
            admin = user_repo.find_first_admin()
            if admin is not None:
                return admin

        user = auth_svc.get_user_from_token(token)
        if user is not None:
            return user
        raise AuthenticationError("Invalid or expired token")

    token = _extract_token_from_request(request)
    if token is None:
        raise AuthenticationError("Not authenticated")

    user = auth_svc.get_user_from_token(token)
    if user is None:
        raise AuthenticationError("Invalid or expired token")
    return user


def get_insight_repo(session: Session = Depends(get_session)) -> IInsightRepository:
    return InsightRepository(session)


def get_insight_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    registry: HookRegistry | None = Depends(get_plugin_registry),
) -> InsightService:
    provider = LLMProviderFactory.create_provider(
        provider_name=settings.llm_provider,
        api_key=settings.llm_api_key,
        api_url=settings.llm_api_url,
    )
    return InsightService(
        uow=uow, provider=provider, model=settings.llm_model, registry=registry
    )


def get_sharing_service(
    uow: SqlUnitOfWork = Depends(get_unit_of_work),
) -> SharingService:
    relationship_svc = RelationshipService(uow)
    key_svc = FederationKeyService(uow)
    discovery_svc = FederationDiscoveryService()
    resolver_svc = FederationDataResolver(
        uow, key_svc, discovery_svc, relationship_svc,
    )
    notify_svc = PeerNotificationService(uow, discovery_svc)
    return SharingService(
        relationship_svc, key_svc, discovery_svc, resolver_svc, notify_svc,
    )


def get_autoregulation_service(
    sleep_svc: SleepAnalysisService = Depends(get_sleep_analysis_service),
    activity_svc: ActivityAnalysisService = Depends(get_activity_analysis_service),
) -> AutoregulationService:
    return AutoregulationService(sleep_svc, activity_svc)


def get_workout_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    autoreg_svc: AutoregulationService = Depends(get_autoregulation_service),
) -> WorkoutService:
    return WorkoutService(uow, autoreg_svc)


def get_backup_provider() -> IBackupStorageProvider:
    from salus.services.backup.providers import (
        LocalBackupProvider,
        WebdavBackupProvider,
    )

    if settings.backup_provider == "webdav":
        if not settings.backup_webdav_url:
            raise ValueError(
                "SALUS_BACKUP_WEBDAV_URL must be configured for WebDAV backup provider."
            )
        return WebdavBackupProvider(
            url=settings.backup_webdav_url,
            username=settings.backup_webdav_username,
            password=settings.backup_webdav_password,
        )
    return LocalBackupProvider(directory=settings.backup_local_dir)


def get_backup_service(
    request: Request,
    provider: IBackupStorageProvider = Depends(get_backup_provider),
) -> BackupService:
    # Retrieve engine and url from request app state if present (for test environments)
    engine = getattr(request.app.state, "engine", None)
    if engine is None:
        from salus.database import engine as prod_engine
        engine = prod_engine
        database_url = settings.database_url
    else:
        database_url = str(engine.url)

    return BackupService(
        engine=engine,
        database_url=database_url,
        password=settings.backup_password,
        provider=provider,
        retention_days=settings.backup_retention_days,
    )


def get_asymmetric_share_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AsymmetricShareService:
    return AsymmetricShareService(uow)


def get_open_science_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> OpenScienceService:
    return OpenScienceService(uow)


def get_circadian_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> CircadianService:
    return CircadianService(uow)


def get_leaderboard_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    sharing_svc: SharingService = Depends(get_sharing_service),
) -> LeaderboardService:
    return LeaderboardService(uow, sharing_svc)


def get_notification_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> NotificationService:
    return NotificationService(uow)


def get_data_portability_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> DataPortabilityService:
    return DataPortabilityService(uow)


def get_event_bus(request: Request) -> EventBus:
    return request.app.state.event_bus


def get_habit_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> HabitService:
    return HabitService(uow)


def get_mood_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> MoodService:
    return MoodService(uow)


def get_journal_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> JournalService:
    return JournalService(uow)


def get_achievement_service(
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> AchievementService:
    return AchievementService(uow)
