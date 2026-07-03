from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from salus.dependencies import get_current_user, get_metric_type_service
from salus.models import DataType
from salus.models.user import User
from salus.schemas import MetricTypeCreate
from salus.services._helpers import uid
from salus.services.metric_type import MetricTypeService

router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def list_metrics(
    request: Request,
    current_user: User = Depends(get_current_user),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    metrics = metric_service.find_all(uid(current_user))
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/metrics.html",
        {"metrics": metrics, "current_user": current_user},
    )


@router.get("/new", response_class=HTMLResponse)
async def new_metric_form(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return request.app.state.templates.TemplateResponse(
        request,
        "components/metric_form.html",
        {"current_user": current_user, "metric": None},
    )


@router.post("")
async def create_metric(
    request: Request,
    name: Annotated[str, Form()],
    unit: Annotated[str, Form()] = "",
    data_type: Annotated[str, Form()] = "number",
    color: Annotated[str, Form()] = "#4f46e5",
    icon: Annotated[str, Form()] = "monitoring",
    current_user: User = Depends(get_current_user),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    metric_service.create(
        MetricTypeCreate(name=name, unit=unit, data_type=DataType(data_type), color=color, icon=icon),
        user_id=uid(current_user),
    )
    return RedirectResponse(url="/metrics", status_code=303)


@router.get("/{metric_type_id}/edit", response_class=HTMLResponse)
async def edit_metric_form(
    metric_type_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    metric = metric_service.get(metric_type_id, uid(current_user))
    return request.app.state.templates.TemplateResponse(
        request,
        "components/metric_form.html",
        {"metric": metric, "current_user": current_user},
    )


@router.put("/{metric_type_id}")
async def update_metric(
    metric_type_id: int,
    name: Annotated[str, Form()],
    unit: Annotated[str, Form()] = "",
    data_type: Annotated[str, Form()] = "number",
    color: Annotated[str, Form()] = "#4f46e5",
    icon: Annotated[str, Form()] = "monitoring",
    current_user: User = Depends(get_current_user),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    metric_service.update(
        metric_type_id,
        uid(current_user),
        MetricTypeCreate(name=name, unit=unit, data_type=DataType(data_type), color=color, icon=icon),
    )
    return RedirectResponse(url="/metrics", status_code=303)


@router.delete("/{metric_type_id}")
async def delete_metric(
    metric_type_id: int,
    current_user: User = Depends(get_current_user),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    metric_service.delete(metric_type_id, uid(current_user))
    return HTMLResponse(status_code=200)
