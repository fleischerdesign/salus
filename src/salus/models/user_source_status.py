from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class UserSourceStatus(SQLModel, table=True):
    __tablename__ = "user_source_status"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True)
    source: str = Field(index=True)
    connected: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    user: "User" = Relationship()  # type: ignore[name-defined]  # noqa: F821
