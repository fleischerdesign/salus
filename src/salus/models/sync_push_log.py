from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class SyncPushLog(SQLModel, table=True):
    __tablename__ = "sync_push_log"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    client_id: str = Field(unique=True, index=True)
    entity: str
    record_id: int
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
