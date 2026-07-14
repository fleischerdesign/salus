from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from salus.services._helpers import uuid7_str


class SyncPushLog(SQLModel, table=True):
    __tablename__ = "sync_push_log"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    client_id: str = Field(unique=True, index=True)
    entity: str
    record_id: str
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
