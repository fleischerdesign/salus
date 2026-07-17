from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class HabitFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY_N = "weekly_n"
    CUSTOM_DAYS = "custom_days"


class Habit(SQLModel, table=True):
    __tablename__ = "habit"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    name: str
    description: str | None = Field(default=None)
    color: str = Field(default="#4f46e5")
    icon: str = Field(default="check-circle")
    frequency: HabitFrequency = Field(default=HabitFrequency.DAILY)
    target_count: int = Field(default=1)
    days_bitmask: int | None = Field(default=None)
    stack_hint: str | None = Field(default=None)
    is_archived: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    user: "User" = Relationship()

    @property
    def active_days(self) -> list[int] | None:
        if self.frequency != HabitFrequency.CUSTOM_DAYS or self.days_bitmask is None:
            return None
        return [i for i in range(7) if (self.days_bitmask >> i) & 1]


class HabitLog(SQLModel, table=True):
    __tablename__ = "habit_log"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    habit_id: str = Field(foreign_key="habit.id")
    user_id: str = Field(foreign_key="user.id")
    log_date: date
    completed: bool = Field(default=False)
    completed_at: datetime | None = Field(default=None)
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = Field(default=None)

    habit: "Habit" = Relationship()
