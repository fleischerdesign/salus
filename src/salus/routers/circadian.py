from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from salus.dependencies import get_current_user, get_circadian_service
from salus.models.user import User
from salus.schemas.circadian import CircadianProfileCreate
from salus.services.circadian import CircadianService
from salus.services._helpers import uid

router = APIRouter(tags=["Circadian Advisor"])


@router.get("/circadian", response_class=HTMLResponse)
async def circadian_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    service: CircadianService = Depends(get_circadian_service),
):
    user_id = uid(current_user)
    profile = service.get_or_create_profile(user_id)
    advice = service.calculate_advice(user_id)
    
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/circadian.html",
        {
            "current_user": current_user,
            "profile": profile,
            "advice": advice,
        },
    )


@router.post("/circadian/profile")
async def save_profile(
    latitude: float = Form(...),
    longitude: float = Form(...),
    timezone_offset_hours: float = Form(...),
    configured_chronotype: str = Form(...),
    current_user: User = Depends(get_current_user),
    service: CircadianService = Depends(get_circadian_service),
):
    profile_data = CircadianProfileCreate(
        latitude=latitude,
        longitude=longitude,
        timezone_offset_hours=timezone_offset_hours,
        configured_chronotype=configured_chronotype
    )
    service.save_profile(user_id=uid(current_user), data=profile_data)
    return RedirectResponse(url="/circadian", status_code=status.HTTP_303_SEE_OTHER)
