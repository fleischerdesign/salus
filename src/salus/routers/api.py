from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from salus.dependencies import (
    get_current_user_or_api,
    get_measurement_service,
    get_metric_type_service,
)
from salus.models.user import User
from salus.schemas import MetricTypeCreate
from salus.schemas.api import EntryResponse, HealthRecordResponse, MetricTypeResponse
from salus.schemas.measurement import MeasurementCreate
from salus.services._helpers import uid
from salus.services.measurement import MeasurementService
from salus.services.metric_type import MetricTypeService

router = APIRouter(prefix="/api/v1")


@router.get("/metrics", response_model=list[MetricTypeResponse])
async def api_list_metrics(
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    return metric_svc.find_all(uid(current_user))


@router.post("/metrics", response_model=MetricTypeResponse, status_code=201)
async def api_create_metric(
    data: MetricTypeCreate,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    result = metric_svc.create(data, uid(current_user))
    assert result.id is not None
    return MetricTypeResponse(
        id=result.id, name=result.name, unit=result.unit,
        data_type=result.data_type, color=result.color,
    )


@router.get("/metrics/{metric_id}", response_model=MetricTypeResponse)
async def api_get_metric(
    metric_id: int,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    result = metric_svc.get(metric_id, uid(current_user))
    assert result.id is not None
    return MetricTypeResponse(
        id=result.id, name=result.name, unit=result.unit,
        data_type=result.data_type, color=result.color,
    )


@router.put("/metrics/{metric_id}", response_model=MetricTypeResponse)
async def api_update_metric(
    metric_id: int,
    data: MetricTypeCreate,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    result = metric_svc.update(metric_id, uid(current_user), data)
    assert result.id is not None
    return MetricTypeResponse(
        id=result.id, name=result.name, unit=result.unit,
        data_type=result.data_type, color=result.color,
    )


@router.delete("/metrics/{metric_id}", status_code=204)
async def api_delete_metric(
    metric_id: int,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    metric_svc.delete(metric_id, uid(current_user))
    return Response(status_code=204)


@router.get("/entries", response_model=list[EntryResponse])
async def api_list_entries(
    metric_type_id: int | None = Query(None),
    current_user: User = Depends(get_current_user_or_api),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    user_id = uid(current_user)
    entries = (
        measurement_svc.find_by_metric_type(metric_type_id, user_id)
        if metric_type_id
        else []
    )
    return [
        EntryResponse(
            id=e.id or 0,
            metric_type_id=e.metric_type_id or 0,
            value=e.display_value,
            timestamp=e.start_time,
            notes=e.notes,
        )
        for e in entries
    ]


@router.post("/entries", response_model=EntryResponse, status_code=201)
async def api_create_entry(
    data: MeasurementCreate,
    metric_type_id: int = Query(...),
    current_user: User = Depends(get_current_user_or_api),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    result = measurement_svc.create(data, metric_type_id, uid(current_user))
    assert result.id is not None
    return EntryResponse(
        id=result.id,
        metric_type_id=result.metric_type_id or 0,
        value=result.display_value,
        timestamp=result.start_time,
        notes=result.notes,
    )


@router.get("/health", response_model=list[HealthRecordResponse])
async def api_list_health(
    data_types: str = Query(None, description="Comma-separated"),
    since: str | None = Query(None),
    until: str | None = Query(None),
    limit: int = Query(100, le=1000),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    types = data_types.split(",") if data_types else None
    dt_since = datetime.fromisoformat(since) if since else None
    dt_until = datetime.fromisoformat(until) if until else None
    records = measurement_svc.repo.find_all(
        data_types=types, since=dt_since, until=dt_until, limit=limit
    )
    return [
        HealthRecordResponse(
            id=str(r.id or 0),
            data_type=r.data_type,
            start_time=r.start_time.isoformat(),
            end_time=r.end_time.isoformat() if r.end_time else "",
            value=r.value_json or r.value_text or str(r.value_numeric or ""),
        )
        for r in records
    ]
