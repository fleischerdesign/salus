from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models.insight import Insight  # noqa: F401
    from salus.models.measurement import Measurement  # noqa: F401
    from salus.models.user import User  # noqa: F401

from salus.services._helpers import DEFAULT_METRIC_COLOR, uuid7_str


class DataType(str, Enum):
    NUMBER = "number"
    TEXT = "text"
    BOOLEAN = "boolean"


class MetricType(SQLModel, table=True):
    __tablename__ = "metric_type"  # pyright: ignore[reportAssignmentType]
    __table_args__ = (UniqueConstraint("name", "user_id"),)

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    name: str
    unit: str = Field(default="")
    data_type: DataType = Field(default=DataType.NUMBER)
    color: str = Field(default=DEFAULT_METRIC_COLOR)
    user_id: str = Field(foreign_key="user.id")
    is_system: bool = Field(default=False)
    source_data_type: str | None = Field(default=None)
    icon: str = Field(default="monitoring")
    widget_size: str = Field(default="medium")
    widget_enabled: bool = Field(default=False)
    position: int = Field(default=0)
    created_at: datetime | None = Field(default=None)
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    user: "User" = Relationship(back_populates="metric_types")
    measurements: list["Measurement"] = Relationship(back_populates="metric_type")
