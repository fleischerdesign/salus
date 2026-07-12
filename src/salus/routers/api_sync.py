import base64
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query

from salus.dependencies import get_current_user, get_unit_of_work
from salus.models.user import User
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.sync import SyncPushRequest, SyncPushResponse
from salus.services.sync import SyncService
from salus.services.write_pipeline import WritePipeline

router = APIRouter(tags=["Sync"])


async def get_sync_service(uow: IUnitOfWork = Depends(get_unit_of_work)) -> SyncService:
    return SyncService(uow)


@router.get("/api/v1/sync")
async def api_sync(
    since: datetime | None = Query(default=None),
    cursor: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: SyncService = Depends(get_sync_service),
):
    if since:
        return service.delta_sync(current_user, since)

    cursors: dict[str, int] | None = None
    if cursor:
        try:
            raw = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
            cursors = {k: int(v) for k, v in raw.items()}
        except (ValueError, json.JSONDecodeError):
            pass
    return service.full_sync(current_user, cursors)


@router.post("/api/v1/sync/push", response_model=SyncPushResponse)
async def api_sync_push(
    body: SyncPushRequest,
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_unit_of_work),
) -> SyncPushResponse:
    pipeline = WritePipeline(uow, current_user)
    results = pipeline.process(body.operations)
    return SyncPushResponse(
        results=results,
        synced_at=datetime.now(timezone.utc).isoformat(),
    )
