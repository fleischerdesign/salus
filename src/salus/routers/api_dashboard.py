from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel

from salus.dependencies import get_current_user, get_dashboard_widget_service
from salus.models.dashboard import WidgetSize
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.dashboard_widget import DashboardWidgetService

router = APIRouter(prefix="/api/v1")


class WidgetCreateResponse(BaseModel):
    id: int
    metric_type_id: int
    size: str


@router.post("/dashboard/widgets", response_model=WidgetCreateResponse, status_code=201)
async def api_create_widget(
    metric_type_id: int = Query(...),
    size: str = Query(default="medium"),
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget = widget_svc.add_widget(uid(current_user), metric_type_id, WidgetSize(size))
    return {"id": widget.id, "metric_type_id": widget.metric_type_id, "size": size}


@router.delete("/dashboard/widgets/{widget_id}", status_code=204)
async def api_delete_widget(
    widget_id: int,
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget_svc.delete_widget(widget_id, uid(current_user))
    return Response(status_code=204)


@router.put("/dashboard/widgets/{widget_id}", response_model=WidgetCreateResponse)
async def api_update_widget(
    widget_id: int,
    size: str = Query(...),
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget = widget_svc.update_widget(widget_id, uid(current_user), WidgetSize(size))
    return {"id": widget.id, "metric_type_id": widget.metric_type_id, "size": size}
