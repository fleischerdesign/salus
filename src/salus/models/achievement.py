from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class AchievementTier(str, Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class AchievementCategory(str, Enum):
    TRACKING = "tracking"
    STREAK = "streak"
    MILESTONE = "milestone"
    GOAL = "goal"
    WORKOUT = "workout"
    HABIT = "habit"
    SOCIAL = "social"
    SPECIAL = "special"


class AchievementDefinition(SQLModel, table=True):
    __tablename__ = "achievement_definition"  # pyright: ignore[reportAssignmentType]

    code: str = Field(primary_key=True)
    title: str
    description: str
    icon: str = Field(default="emoji-events")
    tier: AchievementTier = Field(default=AchievementTier.BRONZE)
    category: AchievementCategory = Field(default=AchievementCategory.TRACKING)
    condition_type: str
    condition_config: str = Field(default="{}")
    is_hidden: bool = Field(default=False)
    sort_order: int = Field(default=0)


class UserAchievement(SQLModel, table=True):
    __tablename__ = "user_achievement"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    achievement_code: str = Field(foreign_key="achievement_definition.code")
    unlocked_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    progress_current: float | None = Field(default=None)
    progress_target: float | None = Field(default=None)
    notified: bool = Field(default=False)

    user: "User" = Relationship()
    achievement_definition: "AchievementDefinition" = Relationship()
