from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from salus.dependencies import (
    get_current_user,
    get_measurement_service,
    get_metric_type_service,
    get_sharing_service,
)
from salus.models.user import User
from salus.schemas.measurement import MeasurementCreate
from salus.services._helpers import uid
from salus.services.measurement import MeasurementService
from salus.services.metric_type import MetricTypeService
from salus.services.sharing import SharingService

router = APIRouter()


def _form_to_create(value: str, timestamp_str: str | None, notes: str | None) -> MeasurementCreate:
    return MeasurementCreate(
        value=value,
        timestamp=datetime.fromisoformat(timestamp_str) if timestamp_str else None,
        notes=notes,
    )


@router.get("", response_class=HTMLResponse)
async def list_entries(
    request: Request,
    metric_type_id: int | None = None,
    current_user: User = Depends(get_current_user),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
    measurement_service: MeasurementService = Depends(get_measurement_service),
):
    user_id = uid(current_user)
    metrics = metric_service.find_all(user_id)
    entries = (
        measurement_service.find_by_metric_type(metric_type_id, user_id)
        if metric_type_id
        else []
    )
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/entries.html",
        {
            "metrics": metrics,
            "entries": entries,
            "selected_metric_id": metric_type_id,
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
        {"metrics": metrics, "selected_metric_id": metric_type_id, "current_user": current_user, "entry": None},
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
            dt = datetime.fromisoformat(timestamp) if timestamp else datetime.now(timezone.utc)
            date_str = dt.date().strftime("%Y-%m-%d")
            sharing_svc.notify_peers_of_update(uid(current_user), metric.source_data_type, date_str)
    except Exception:
        pass

    return RedirectResponse(
        url=f"/entries?metric_type_id={metric_type_id}", status_code=303
    )


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
