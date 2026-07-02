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
)
from salus.repositories.system_config import SystemConfigRepository
from salus.repositories.user import UserRepository
from salus.repositories.user_identity import UserIdentityRepository
from salus.repositories.sharing import SharingRepository


class IUnitOfWork(Protocol):
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

    def __enter__(self) -> "IUnitOfWork":
        ...

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...


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
