from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
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

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    metric_type_id: int = Field(foreign_key="metric_type.id")
    target_value: float
    direction: GoalDirection = Field(default=GoalDirection.INCREASE)
    frequency: GoalFrequency = Field(default=GoalFrequency.DAILY)
    deadline: date | None = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="goals")
