from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from salus.dependencies import (
    get_current_user,
    get_measurement_service,
    get_metric_type_service,
    get_sharing_service,
)
from salus.models import DataType
from salus.models.user import User
from salus.schemas import MetricTypeCreate
from salus.schemas.measurement import MeasurementCreate
from salus.services._helpers import uid
from salus.services.measurement import MeasurementService
from salus.services.metric_type import MetricTypeService
from salus.services.sharing import SharingService

router = APIRouter()


def _form_to_create(
    value: str, timestamp_str: str | None, notes: str | None
) -> MeasurementCreate:
    return MeasurementCreate(
        value=value,
        timestamp=datetime.fromisoformat(timestamp_str) if timestamp_str else None,
        notes=notes,
    )


# ── Entry routes ─────────────────────────────────────────────────


@router.get("", response_class=HTMLResponse)
async def entries_overview(
    request: Request,
    current_user: User = Depends(get_current_user),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    user_id = uid(current_user)
    metrics = metric_svc.find_all(user_id)
    metric_ids = [m.id for m in metrics if m.id is not None]
    overview = (
        measurement_svc.get_metric_overview(user_id, metric_ids) if metric_ids else {}
    )
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/entries.html",
        {
            "metrics": metrics,
            "overview": overview,
            "current_user": current_user,
        },
    )


@router.get("/new", response_class=HTMLResponse)
async def new_entry_form(
    request: Request,
    metric_type_id: int | None = None,
    current_user: User = Depends(get_current_user),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    metrics = metric_service.find_all(uid(current_user))
    return request.app.state.templates.TemplateResponse(
        request,
        "components/entry_form.html",
        {
            "metrics": metrics,
            "selected_metric_id": metric_type_id,
            "current_user": current_user,
            "entry": None,
        },
    )


@router.post("")
async def create_entry(
    request: Request,
    value: str = Form(...),
    metric_type_id: int = Form(...),
    timestamp: str | None = Form(None),
    notes: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    measurement_service: MeasurementService = Depends(get_measurement_service),
    sharing_svc: SharingService = Depends(get_sharing_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    measurement_service.create(
        _form_to_create(value, timestamp, notes),
        metric_type_id,
        uid(current_user),
    )
    try:
        metric = metric_svc.get(metric_type_id, uid(current_user))
        if metric and metric.source_data_type:
            dt = (
                datetime.fromisoformat(timestamp)
                if timestamp
                else datetime.now(timezone.utc)
            )
            date_str = dt.date().strftime("%Y-%m-%d")
            sharing_svc.notify_peers_of_update(
                uid(current_user), metric.source_data_type, date_str
            )
    except Exception:
        pass

    return RedirectResponse(url=f"/entries/{metric_type_id}", status_code=303)


@router.get("/{entry_id}/edit", response_class=HTMLResponse)
async def edit_entry_form(
    entry_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    measurement_service: MeasurementService = Depends(get_measurement_service),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    entry = measurement_service.get(entry_id, uid(current_user))
    metrics = metric_service.find_all(uid(current_user))
    return request.app.state.templates.TemplateResponse(
        request,
        "components/entry_form.html",
        {"entry": entry, "metrics": metrics, "current_user": current_user},
    )


@router.put("/{entry_id}")
async def update_entry(
    entry_id: int,
    value: str = Form(...),
    timestamp: str | None = Form(None),
    notes: str | None = Form(None),
    current_user: User = Depends(get_current_user),
    measurement_service: MeasurementService = Depends(get_measurement_service),
):
    measurement_service.update(
        entry_id,
        uid(current_user),
        _form_to_create(value, timestamp, notes),
    )
    return RedirectResponse(url="/entries", status_code=303)


@router.delete("/{entry_id}")
async def delete_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    measurement_service: MeasurementService = Depends(get_measurement_service),
):
    measurement_service.delete(entry_id, uid(current_user))
    return HTMLResponse(status_code=200)


@router.get("/{metric_type_id}", response_class=HTMLResponse)
async def entries_detail(
    metric_type_id: int,
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=10, le=100),
    current_user: User = Depends(get_current_user),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    user_id = uid(current_user)
    metric = metric_svc.get(metric_type_id, user_id)

    is_htmx = request.headers.get("HX-Request")

    entries, total, total_pages = measurement_svc.find_by_metric_type_paginated(
        metric_type_id,
        user_id,
        page=page,
        per_page=limit,
    )

    context = {
        "metric": metric,
        "entries": entries,
        "current_page": page,
        "total_pages": total_pages,
        "total_entries": total,
        "url_pattern": f"/entries/{metric_type_id}?limit={limit}&page={{page}}",
        "current_user": current_user,
    }

    template = (
        "components/entries_table_partial.html"
        if is_htmx
        else "pages/entries_detail.html"
    )
    return request.app.state.templates.TemplateResponse(request, template, context)


# ── Metric admin routes ───────────────────────────────────────────


@router.get("/metric/new", response_class=HTMLResponse)
async def new_metric_form(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return request.app.state.templates.TemplateResponse(
        request,
        "components/metric_form.html",
        {"current_user": current_user, "metric": None},
    )


@router.post("/metric")
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
        MetricTypeCreate(
            name=name, unit=unit, data_type=DataType(data_type), color=color, icon=icon
        ),
        user_id=uid(current_user),
    )
    return RedirectResponse(url="/entries", status_code=303)


@router.get("/metric/{metric_type_id}/edit", response_class=HTMLResponse)
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


@router.put("/metric/{metric_type_id}")
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
        MetricTypeCreate(
            name=name, unit=unit, data_type=DataType(data_type), color=color, icon=icon
        ),
    )
    return RedirectResponse(url="/entries", status_code=303)


@router.delete("/metric/{metric_type_id}")
async def delete_metric(
    metric_type_id: int,
    current_user: User = Depends(get_current_user),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    metric_service.delete(metric_type_id, uid(current_user))
    return HTMLResponse(status_code=200)


@router.post("/metric/reorder")
async def reorder_metrics(
    ids: str = Form(),
    current_user: User = Depends(get_current_user),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    ordered = [int(i) for i in ids.split(",") if i.strip().isdigit()]
    metric_service.reorder(uid(current_user), ordered)
    return Response(status_code=204)
