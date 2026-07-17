from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class MoodTagCategory(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class MoodTag(SQLModel, table=True):
    __tablename__ = "mood_tag"  # pyright: ignore[reportAssignmentType]

    code: str = Field(primary_key=True)
    label: str
    emoji: str | None = Field(default=None)
    category: MoodTagCategory = Field(default=MoodTagCategory.NEUTRAL)
    is_system: bool = Field(default=True)


class MoodEntry(SQLModel, table=True):
    __tablename__ = "mood_entry"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    entry_date: date
    mood_score: int = Field(ge=1, le=10)
    energy_level: int | None = Field(default=None, ge=1, le=10)
    stress_level: int | None = Field(default=None, ge=1, le=10)
    tag_codes: str | None = Field(default=None)
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    user: "User" = Relationship()
