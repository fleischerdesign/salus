from fastapi import APIRouter, Depends
from pydantic import BaseModel

from salus.dependencies import get_current_user, get_dashboard_widget_service
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
