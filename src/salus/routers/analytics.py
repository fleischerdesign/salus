from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse

from salus.dependencies import (
    get_analytics_service,
    get_current_user,
)
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.analytics.orchestrator import AnalyticsService

router = APIRouter()


@router.get("/analytics", response_class=HTMLResponse)
async def analytics_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    ctx = analytics_svc.build_context(user_id=uid(current_user), range_key="30d")
    ctx["current_user"] = current_user
    ctx["active_range"] = "30d"
    return request.app.state.templates.TemplateResponse(
        request, "pages/analytics.html", ctx
    )


@router.get("/analytics/data", response_class=HTMLResponse)
async def analytics_data(
    request: Request,
    range: str = Query("30d"),
    current_user: User = Depends(get_current_user),
    analytics_svc: AnalyticsService = Depends(get_analytics_service),
):
    ctx = analytics_svc.build_context(user_id=uid(current_user), range_key=range)
    ctx["active_range"] = range
    return request.app.state.templates.TemplateResponse(
        request, "components/analytics/grid.html", ctx
    )
