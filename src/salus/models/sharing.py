from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401
    from salus.models import MetricType  # noqa: F401


class SharingRelationship(SQLModel, table=True):
    __tablename__ = "sharing_relationship"  # pyright: ignore[reportAssignmentType]

    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id")
    grantee_handle: str
    metric_type_id: int = Field(foreign_key="metric_type.id")
    aggregation_level: str = Field(default="daily_summary")  # "raw" or "daily_summary"
    expiration_date: Optional[datetime] = Field(default=None)
    is_active: bool = Field(default=True)
    api_token_hash: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    owner: "User" = Relationship(back_populates="sharing_relationships")
    metric_type: "MetricType" = Relationship()
