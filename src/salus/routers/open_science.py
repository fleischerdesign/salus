from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from salus.dependencies import get_current_user, get_open_science_service
from salus.models.user import User
from salus.schemas.open_science import OpenScienceSynthesizeRequest
from salus.services.open_science import OpenScienceService
from salus.services._helpers import uid

router = APIRouter(tags=["Open Science"])


@router.get("/open-science", response_class=HTMLResponse)
async def open_science_page(request: Request):
    return RedirectResponse(url="/settings/shares", status_code=307)


@router.post("/api/v1/open-science/synthesize", response_class=JSONResponse)
async def synthesize_data(
    data: OpenScienceSynthesizeRequest,
    current_user: User = Depends(get_current_user),
    service: OpenScienceService = Depends(get_open_science_service),
):
    try:
        payload = service.synthesize(user_id=uid(current_user), req=data)
        return payload
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)}
        )
