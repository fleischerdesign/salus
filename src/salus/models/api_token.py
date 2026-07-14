from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401

AVAILABLE_SCOPES = [
    ("ingest:write", "Webhook data ingestion"),
    ("entries:read", "Read manual entries"),
    ("entries:write", "Create/edit/delete entries"),
    ("metrics:read", "Read metric types"),
    ("metrics:write", "Create/edit/delete metrics"),
    ("goals:read", "Read goals"),
    ("goals:write", "Create/edit/delete goals"),
    ("health:read", "Query health data (analytics/export)"),
    ("admin", "Full administrative access"),
]


class ApiToken(SQLModel, table=True):
    __tablename__ = "api_token"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    token_hash: str = Field(unique=True, index=True)
    token_prefix: str
    label: str
    scopes: str = Field(default="")
    user_id: str = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used_at: datetime | None = Field(default=None)
    is_active: bool = Field(default=True)

    user: "User" = Relationship()  # type: ignore[name-defined]  # noqa: F821

    def has_scope(self, scope: str) -> bool:
        scope_set = set(self.scopes.split())
        return "admin" in scope_set or scope in scope_set
