from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from salus.dependencies import (
    get_current_user,
    get_dashboard_service,
    get_measurement_service,
    get_metric_type_service,
)
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.analytics.dashboard import DashboardService
from salus.services.measurement import MeasurementService
from salus.services.metric_type import MetricTypeService

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    dashboard_svc: DashboardService = Depends(get_dashboard_service),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
    measurement_service: MeasurementService = Depends(get_measurement_service),
):
    user_id = uid(current_user)
    metrics = metric_service.find_all(user_id)
    entries_by_metric: dict[int | None, list] = {}
    for metric in metrics:
        assert metric.id is not None
        entries_by_metric[metric.id] = measurement_service.find_by_metric_type(
            metric.id, user_id
        )
    dashboard_summary = dashboard_svc.summary()
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/dashboard.html",
        {
            "metrics": metrics,
            "entries_by_metric": entries_by_metric,
            "current_user": current_user,
            "dashboard": dashboard_summary,
        },
    )
