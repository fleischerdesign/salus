from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class UserIdentity(SQLModel, table=True):
    __tablename__ = "user_identity"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    provider: str
    provider_user_id: str
    provider_data: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="identities")
