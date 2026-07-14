import base64
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from salus.dependencies import get_current_user, get_event_bus, get_unit_of_work
from salus.repositories.entity_meta import ENTITY_META
from salus.models.user import User
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.sync import SyncPushRequest, SyncPushResponse
from salus.services._helpers import uid
from salus.services.event_bus import EventBus
from salus.services.sync import SyncService
from salus.services.write_pipeline import WritePipeline
from salus.services.command_registry import list_commands

SYNC_PROTOCOL_VERSION = 1

router = APIRouter(tags=["Sync"])


def _check_sync_version(
    x_salus_sync_version: int = Header(default=SYNC_PROTOCOL_VERSION, alias="X-Salus-Sync-Version"),
) -> int:
    if x_salus_sync_version != SYNC_PROTOCOL_VERSION:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported sync protocol version. Expected {SYNC_PROTOCOL_VERSION}, got {x_salus_sync_version}",
        )
    return x_salus_sync_version


async def get_sync_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> SyncService:
    return SyncService(uow)


@router.get("/api/v1/sync")
async def api_sync(
    since: datetime | None = Query(default=None),
    cursor: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: SyncService = Depends(get_sync_service),
    _version: int = Depends(_check_sync_version),
):
    if since:
        result = service.delta_sync(current_user, since)
        result["sync_version"] = SYNC_PROTOCOL_VERSION
        return result

    cursors: dict[str, str] | None = None
    if cursor:
        try:
            raw = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
            cursors = {k: str(v) for k, v in raw.items()}
        except (ValueError, json.JSONDecodeError):
            pass
    result = service.full_sync(current_user, cursors)
    result["sync_version"] = SYNC_PROTOCOL_VERSION
    return result


@router.post("/api/v1/sync/push", response_model=SyncPushResponse)
async def api_sync_push(
    body: SyncPushRequest,
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_unit_of_work),
    event_bus: EventBus = Depends(get_event_bus),
    _version: int = Depends(_check_sync_version),
) -> SyncPushResponse:
    pipeline = WritePipeline(uow, current_user)
    results = pipeline.process(body.operations)
    await event_bus.publish(uid(current_user))
    return SyncPushResponse(
        results=results,
        synced_at=datetime.now(timezone.utc).isoformat(),
        sync_version=SYNC_PROTOCOL_VERSION,
    )


class SyncEntityInfo(BaseModel):
    name: str
    strategy: str


class SyncManifest(BaseModel):
    entities: list[SyncEntityInfo]
    commands: list[str]


@router.get("/api/v1/sync/entities", response_model=SyncManifest)
async def api_sync_entities(
    current_user: User = Depends(get_current_user),
    _version: int = Depends(_check_sync_version),
) -> SyncManifest:
    entities = [
        SyncEntityInfo(name=e.name, strategy=e.strategy)
        for e in ENTITY_META
    ]
    return SyncManifest(entities=entities, commands=list_commands())


@router.get("/api/v1/sync/events")
async def api_sync_events(
    request: Request,
    current_user: User = Depends(get_current_user),
    event_bus: EventBus = Depends(get_event_bus),
    _version: int = Depends(_check_sync_version),
):
    async def event_generator():
        async for _ in event_bus.subscribe(uid(current_user)):
            if await request.is_disconnected():
                break
            yield "event: sync\ndata: \n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
