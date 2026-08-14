from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel

from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class DataQualityKind(str, Enum):
    HARD_BOUND = "hard_bound"
    CROSS_SOURCE = "cross_source"
    ANOMALY = "anomaly"


class DataQualitySeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"


class DataQualityFlag(SQLModel, table=True):
    __tablename__ = "data_quality_flag"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    kind: str = Field(index=True)
    metric_code: str | None = Field(default=None, foreign_key="metric_definition.code")
    measurement_id: str | None = Field(default=None, index=True)
    severity: str = Field(default=DataQualitySeverity.WARNING)
    message: str
    context_json: str | None = Field(default=None)
    resolved_at: datetime | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
