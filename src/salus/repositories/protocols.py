from datetime import datetime
from typing import Protocol, TypeVar, runtime_checkable

from salus.models.api_token import ApiToken
from salus.models.dashboard import DashboardWidget
from salus.models.goal import Goal
from salus.models.measurement import Measurement
from salus.models import MetricType
from salus.models.system_config import SystemConfig
from salus.models.user import User
from salus.models.user_identity import UserIdentity

T = TypeVar("T")


@runtime_checkable
class IRepository(Protocol[T]):
    def get_by_id(self, id: int) -> T | None:
        ...

    def create(self, obj: T) -> T:
        ...

    def update(self, obj: T) -> T:
        ...

    def delete(self, obj: T) -> None:
        ...

    def add(self, obj: T) -> None:
        ...

    def add_all(self, objs: list[T]) -> None:
        ...

    def commit(self) -> None:
        ...


@runtime_checkable
class IUserRepository(IRepository[User], Protocol):
    def get_by_username(self, username: str) -> User | None:
        ...

    def get_by_email(self, email: str) -> User | None:
        ...

    def find_first_admin(self) -> User | None:
        ...

    def list_all(self) -> list[User]:
        ...

    def toggle_admin(self, user_id: int) -> User:
        ...

    def toggle_active(self, user_id: int) -> User:
        ...


@runtime_checkable
class IUserIdentityRepository(IRepository[UserIdentity], Protocol):
    def get_by_provider_user_id(self, provider: str, provider_user_id: str) -> UserIdentity | None:
        ...

    def list_by_user(self, user_id: int) -> list[UserIdentity]:
        ...


@runtime_checkable
class IMeasurementRepository(IRepository[Measurement], Protocol):
    def find_by_metric_type(
        self, metric_type_id: int, user_id: int | None = None
    ) -> list[Measurement]:
        ...

    def find_all(
        self,
        user_id: int | None = None,
        data_types: list[str] | None = None,
        sources: list[str] | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
    ) -> list[Measurement]:
        ...

    def find_latest(self, data_type: str, user_id: int | None = None) -> Measurement | None:
        ...

    def upsert_all(self, records: list[Measurement]) -> tuple[int, int]:
        ...

    def find_by_date_range(
        self, user_id: int, data_types: list[str], since: datetime, until: datetime
    ) -> list[Measurement]:
        ...

    def find_recent_entries(
        self, user_id: int, limit: int = 20
    ) -> list[Measurement]:
        ...


@runtime_checkable
class IMetricTypeRepository(IRepository[MetricType], Protocol):
    def find_all(self, user_id: int | None = None) -> list[MetricType]:
        ...

    def find_by_name(self, name: str) -> MetricType | None:
        ...

    def find_by_name_and_user(self, name: str, user_id: int) -> MetricType | None:
        ...


@runtime_checkable
class IGoalRepository(IRepository[Goal], Protocol):
    def find_by_user(self, user_id: int) -> list[Goal]:
        ...

    def find_all_goals(self) -> list[Goal]:
        ...


@runtime_checkable
class IApiTokenRepository(IRepository[ApiToken], Protocol):
    def find_by_user(self, user_id: int) -> list[ApiToken]:
        ...

    def find_all_by_user(self, user_id: int) -> list[ApiToken]:
        ...

    def find_by_prefix(self, token_prefix: str) -> list[ApiToken]:
        ...

    def list_all_active(self) -> list[ApiToken]:
        ...

    def record_usage(self, token: ApiToken) -> None:
        ...


@runtime_checkable
class ISystemConfigRepository(IRepository[SystemConfig], Protocol):
    def get_all(self) -> list[SystemConfig]:
        ...

    def get_by_key(self, key: str) -> SystemConfig | None:
        ...

    def upsert(self, key: str, value: str, **kwargs) -> SystemConfig:
        ...

    def seed_missing(self, defaults: list[SystemConfig]) -> int:
        ...


@runtime_checkable
class IDashboardWidgetRepository(IRepository[DashboardWidget], Protocol):
    def find_by_user(self, user_id: int) -> list[DashboardWidget]:
        ...

    def reorder(self, user_id: int, ordered_ids: list[int]) -> None:
        ...

    def find_by_user_and_metric(self, user_id: int, metric_type_id: int) -> DashboardWidget | None:
        ...
