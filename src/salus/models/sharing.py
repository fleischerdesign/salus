from enum import Enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401
    from salus.models import MetricType  # noqa: F401


class ConnectionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DECLINED = "declined"
    REVOKED = "revoked"


class SharingRelationship(SQLModel, table=True):
    __tablename__ = "sharing_relationship"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    grantee_handle: str
    metric_type_id: int = Field(foreign_key="metric_type.id")
    aggregation_level: str = Field(default="daily_summary")  # "raw" or "daily_summary"
    expiration_date: Optional[datetime] = Field(default=None)
    status: str = Field(default=ConnectionStatus.PENDING.value)
    api_token_hash: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_active(self) -> bool:
        return self.status == ConnectionStatus.ACTIVE

    # Relationships
    owner: "User" = Relationship(back_populates="sharing_relationships")
    metric_type: "MetricType" = Relationship()


class LeaderboardGroup(SQLModel, table=True):
    __tablename__ = "leaderboard_group"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    creator_id: int = Field(foreign_key="user.id")
    metric_type_code: str = Field(default="steps")  # "steps", "workouts", "sleep", "water"
    time_frame: str = Field(default="weekly")  # "weekly", "monthly", "custom"
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    invite_code: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    creator: "User" = Relationship()
    members: list["LeaderboardMember"] = Relationship(back_populates="group", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class LeaderboardMember(SQLModel, table=True):
    __tablename__ = "leaderboard_member"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="leaderboard_group.id")
    user_handle: str = Field(index=True)  # @username or @username:domain
    status: str = Field(default="active")  # "pending", "active", "declined"
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    group: "LeaderboardGroup" = Relationship(back_populates="members")
