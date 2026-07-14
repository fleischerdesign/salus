from typing import Any

from pydantic import BaseModel, Field


class SyncOperation(BaseModel):
    type: str = Field(..., description="create | update | delete | command")
    entity: str | None = None
    id: str | None = Field(default=None, description="Required for update/delete")
    client_id: str | None = Field(default=None, description="Client-generated dedup ID")
    data: dict[str, Any] | None = Field(default=None, description="Entity fields for create/update")
    expected_updated_at: str | None = Field(default=None, description="Optimistic locking timestamp")
    command: str | None = Field(default=None, description="Command name for type='command'")
    payload: dict[str, Any] | None = Field(default=None, description="Command payload for type='command'")


class SyncResult(BaseModel):
    type: str = Field(default="create")
    entity: str = ""
    client_id: str | None = None
    id: str | None = None
    status: str = Field(default="created", description="created | updated | deleted | not_found | conflict | forbidden | error")
    record: dict[str, Any] | None = None
    conflict: dict[str, Any] | None = None
    message: str | None = None
    command: str | None = None


class SyncPushRequest(BaseModel):
    operations: list[SyncOperation]


class SyncPushResponse(BaseModel):
    results: list[SyncResult]
    synced_at: str
    sync_version: int = 1
