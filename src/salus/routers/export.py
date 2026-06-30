import io

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse

from salus.dependencies import (
    get_current_user,
    get_export_service,
)
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.export import ExportService

router = APIRouter()


@router.get("/export/download")
async def export_download(
    format: str = Query("csv", description="csv | json"),
    since: str | None = Query(None),
    until: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    export_svc: ExportService = Depends(get_export_service),
):
    user_id = uid(current_user)
    content, filename, media_type = export_svc.export_all(
        user_id, format=format, since=since, until=until
    )
    return StreamingResponse(
        io.StringIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
