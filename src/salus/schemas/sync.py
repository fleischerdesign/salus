from typing import Any

from pydantic import BaseModel, Field


class SyncOperation(BaseModel):
    type: str = Field(..., description="create | update | delete")
    entity: str
    id: int | None = Field(default=None, description="Required for update/delete")
    client_id: str | None = Field(default=None, description="Client-generated ID for temp-ID resolution")
    data: dict[str, Any] | None = Field(default=None, description="Entity fields for create/update")
    expected_updated_at: str | None = Field(default=None, description="Optimistic locking timestamp")


class SyncResult(BaseModel):
    type: str = Field(default="create")
    entity: str = ""
    client_id: str | None = None
    id: int | None = None
    status: str = Field(default="created", description="created | updated | deleted | not_found | conflict | forbidden | error")
    record: dict[str, Any] | None = None
    conflict: dict[str, Any] | None = None
    message: str | None = None


class SyncPushRequest(BaseModel):
    operations: list[SyncOperation]


class SyncPushResponse(BaseModel):
    results: list[SyncResult]
    synced_at: str
    sync_version: int = 1
