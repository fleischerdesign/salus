from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel

from salus.dependencies import get_current_user, get_dashboard_widget_service
from salus.models.dashboard import WidgetSize
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.dashboard_widget import DashboardWidgetService

router = APIRouter(prefix="/api/v1")


class WidgetResponse(BaseModel):
    id: str
    widget_type: str = "metric"
    metric_code: str | None = None
    size: str
    position: int
    config_json: str

    model_config = {"from_attributes": True}


class WidgetCreateResponse(BaseModel):
    id: str
    widget_type: str = "metric"
    metric_code: str | None = None
    size: str


@router.get("/dashboard/widgets", response_model=list[WidgetResponse])
async def api_list_widgets(
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widgets = widget_svc.list_widgets(uid(current_user))
    return widgets


@router.get("/dashboard/widgets/{widget_id}/data", response_model=dict)
async def api_widget_data(
    widget_id: str,
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget = widget_svc.get_widget(widget_id, uid(current_user))
    viz = widget_svc.widget_data(widget, uid(current_user))
    return viz.__dict__


@router.post("/dashboard/widgets", response_model=WidgetCreateResponse, status_code=201)
async def api_create_widget(
    widget_type: str = Query(default="metric"),
    metric_code: str | None = Query(default=None),
    size: str = Query(default="medium"),
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget = widget_svc.add_widget(uid(current_user), widget_type, metric_code, WidgetSize(size))
    return {"id": widget.id, "widget_type": widget.widget_type, "metric_code": widget.metric_code, "size": size}


@router.delete("/dashboard/widgets/{widget_id}", status_code=204)
async def api_delete_widget(
    widget_id: str,
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget_svc.delete_widget(widget_id, uid(current_user))
    return Response(status_code=204)


@router.put("/dashboard/widgets/{widget_id}", response_model=WidgetCreateResponse)
async def api_update_widget(
    widget_id: str,
    size: str = Query(...),
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget = widget_svc.update_widget(widget_id, uid(current_user), WidgetSize(size))
    return {"id": widget.id, "widget_type": widget.widget_type, "metric_code": widget.metric_code, "size": size}

