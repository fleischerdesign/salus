from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models import MetricType  # noqa: F401
    from salus.models.goal import Goal  # noqa: F401
    from salus.models.measurement import Measurement  # noqa: F401
    from salus.models.user_identity import UserIdentity  # noqa: F401


class User(SQLModel, table=True):
    __tablename__ = "user"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str | None = Field(default=None)
    email: str | None = Field(default=None, unique=True)
    display_name: str | None = Field(default=None)
    is_admin: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    metric_types: list["MetricType"] = Relationship(back_populates="user")
    measurements: list["Measurement"] = Relationship(back_populates="user")
    identities: list["UserIdentity"] = Relationship(back_populates="user")
    goals: list["Goal"] = Relationship(back_populates="user")
