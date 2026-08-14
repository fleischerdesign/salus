from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class NotificationCategory(str, Enum):
    SYSTEM = "system"
    FEDERATION = "federation"
    CHALLENGE = "challenge"
    DATA_QUALITY = "data_quality"


class NotificationSeverity(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    CRITICAL = "critical"


class Notification(SQLModel, table=True):
    __tablename__ = "notification"  # pyright: ignore[reportAssignmentType]

    id: Optional[str] = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    title: str
    message: str
    is_read: bool = Field(default=False)
    category: str = Field(default=NotificationCategory.SYSTEM)
    severity: str = Field(default=NotificationSeverity.INFO)
    link: str | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    user: "User" = Relationship(back_populates="notifications")
