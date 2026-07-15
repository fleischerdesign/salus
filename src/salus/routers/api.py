
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from salus.dependencies import (
    get_current_user_or_api,
    get_measurement_service,
    get_metric_type_service,
)
from salus.models.user import User
from salus.schemas import MetricTypeCreate
from salus.schemas.api import (
    EntryListResponse,
    EntryResponse,
    EntryUpdate,
    MetricTypeResponse,
)
from salus.schemas.measurement import MeasurementCreate
from salus.services._helpers import uid
from salus.services.measurement import MeasurementService
from salus.services.metric_type import MetricTypeService

router = APIRouter(prefix="/api/v1")


def _metric_response(m) -> MetricTypeResponse:
    return MetricTypeResponse(
        id=m.id,
        name=m.name,
        unit=m.unit,
        data_type=m.data_type,
        color=m.color,
        icon=m.icon,
        is_system=m.is_system,
    )


def _entry_response(e) -> EntryResponse:
    return EntryResponse(
        id=e.id or "",
        metric_type_id=e.metric_type_id or "",
        value=e.display_value,
        timestamp=e.start_time,
        notes=e.notes,
    )


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


@router.get("/metrics", response_model=list[MetricTypeResponse])
async def api_list_metrics(
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    return [_metric_response(m) for m in metric_svc.find_all(uid(current_user))]


@router.post("/metrics", response_model=MetricTypeResponse, status_code=201)
async def api_create_metric(
    data: MetricTypeCreate,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    result = metric_svc.create(data, uid(current_user))
    return _metric_response(result)



@router.get("/metrics/{metric_id}", response_model=MetricTypeResponse)
async def api_get_metric(
    metric_id: str,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    result = metric_svc.get(metric_id, uid(current_user))
    return _metric_response(result)


@router.put("/metrics/{metric_id}", response_model=MetricTypeResponse)
async def api_update_metric(
    metric_id: str,
    data: MetricTypeCreate,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    result = metric_svc.update(metric_id, uid(current_user), data)
    return _metric_response(result)


@router.delete("/metrics/{metric_id}", status_code=204)
async def api_delete_metric(
    metric_id: str,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    metric_svc.delete(metric_id, uid(current_user))
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Entries
# ---------------------------------------------------------------------------


@router.get("/entries", response_model=EntryListResponse)
async def api_list_entries(
    metric_type_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user_or_api),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    user_id = uid(current_user)
    if not metric_type_id:
        return EntryListResponse(
            entries=[], total=0, page=page, per_page=per_page, total_pages=1
        )
    entries, total, total_pages = measurement_svc.find_by_metric_type_paginated(
        metric_type_id, user_id, page=page, per_page=per_page
    )
    return EntryListResponse(
        entries=[_entry_response(e) for e in entries],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.post("/entries", response_model=EntryResponse, status_code=201)
async def api_create_entry(
    data: MeasurementCreate,
    metric_type_id: str = Query(...),
    current_user: User = Depends(get_current_user_or_api),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    result = measurement_svc.create(data, metric_type_id, uid(current_user))
    return _entry_response(result)


@router.put("/entries/{entry_id}", response_model=EntryResponse)
async def api_update_entry(
    entry_id: str,
    data: EntryUpdate,
    current_user: User = Depends(get_current_user_or_api),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    existing = measurement_svc.get(entry_id, uid(current_user))
    create_data = MeasurementCreate(
        value=data.value if data.value is not None else existing.display_value,
        timestamp=data.timestamp,
        notes=data.notes,
    )
    result = measurement_svc.update(entry_id, uid(current_user), create_data)
    return _entry_response(result)


@router.delete("/entries/{entry_id}", status_code=204)
async def api_delete_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user_or_api),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    measurement_svc.delete(entry_id, uid(current_user))
    return Response(status_code=204)
