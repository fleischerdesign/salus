from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import DEFAULT_METRIC_COLOR, uuid7_str

if TYPE_CHECKING:
    from salus.models.metric_definition import MetricDefinition  # noqa: F401
    from salus.models.user import User  # noqa: F401


class UserMetricPreference(SQLModel, table=True):
    __tablename__ = "user_metric_preference"  # pyright: ignore[reportAssignmentType]
    __table_args__ = (UniqueConstraint("user_id", "metric_code"),)

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    metric_code: str = Field(foreign_key="metric_definition.code")
    enabled: bool = Field(default=True)
    color: str = Field(default=DEFAULT_METRIC_COLOR)
    icon: str = Field(default="monitoring")
    widget_size: str = Field(default="medium")
    widget_enabled: bool = Field(default=False)
    position: int = Field(default=0)

    user: "User" = Relationship(back_populates="metric_preferences")
    metric_definition: "MetricDefinition" = Relationship(back_populates="preferences")
