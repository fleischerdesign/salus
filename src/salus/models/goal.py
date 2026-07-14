from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import uuid7_str

if TYPE_CHECKING:
    from salus.models import MetricType  # noqa: F401
    from salus.models.user import User  # noqa: F401


class GoalDirection(str, Enum):
    INCREASE = "increase"
    DECREASE = "decrease"


class GoalFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ONCE = "once"


class Goal(SQLModel, table=True):
    __tablename__ = "goal"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    metric_type_id: str = Field(foreign_key="metric_type.id")
    target_value: float
    direction: GoalDirection = Field(default=GoalDirection.INCREASE)
    frequency: GoalFrequency = Field(default=GoalFrequency.DAILY)
    deadline: date | None = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    user: "User" = Relationship(back_populates="goals")
    metric_type: "MetricType" = Relationship()  # type: ignore[name-defined]  # noqa: F821
