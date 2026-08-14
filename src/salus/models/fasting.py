from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, SQLModel

from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class FastingSession(SQLModel, table=True):
    __tablename__ = "fasting_session"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str | None = Field(default=None, foreign_key="user.id", index=True)
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ended_at: datetime | None = Field(default=None)
    target_hours: float = Field(default=16.0)
    fasting_type: str = Field(default="intermittent")
    water_only: bool = Field(default=True)
    notes: str | None = Field(default=None)
    mood_during: int | None = Field(default=None)
    difficulty: int | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)


class FastingProtocol(SQLModel, table=True):
    __tablename__ = "fasting_protocol"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str | None = Field(default=None, foreign_key="user.id", index=True)
    name: str
    fasting_hours: float = Field(default=16.0)
    eating_window_hours: float = Field(default=8.0)
    schedule_type: str = Field(default="daily")
    target_days_per_week: int | None = Field(default=None)
    is_default: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)
