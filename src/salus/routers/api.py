
from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from salus.dependencies import (
    get_current_user_or_api,
    get_measurement_service,
    get_metric_definition_service,
    get_metric_group_service,
)
from salus.models import DataType
from salus.models.user import User
from salus.schemas import MetricPreferenceCreate
from salus.schemas.api import (
    EntryListResponse,
    EntryResponse,
    EntryUpdate,
    MetricGroupResponse,
    MetricTypeResponse,
)
from salus.schemas.measurement import MeasurementCreate
from salus.services._helpers import uid
from salus.services.measurement import MeasurementService
from salus.services.metric_definition import MetricDefinitionService
from salus.services.metric_group import MetricGroupService

router = APIRouter(prefix="/api/v1")


def _metric_response(m) -> MetricTypeResponse:
    from salus.models.metric_definition import MetricDefinition
    from salus.models.metric_preference import UserMetricPreference

    if isinstance(m, MetricDefinition):
        return MetricTypeResponse(
            id=m.code,
            name=m.name,
            unit=m.unit,
            data_type=m.data_type,
            color="#4f46e5",
            icon="monitoring",
            is_system=True,
        )
    if isinstance(m, UserMetricPreference):
        return MetricTypeResponse(
            id=m.metric_code,
            name=m.metric_definition.name if m.metric_definition else m.metric_code,
            unit=m.metric_definition.unit if m.metric_definition else "",
            data_type=m.metric_definition.data_type if m.metric_definition else DataType.NUMBER,
            color=m.color,
            icon=m.icon,
            is_system=True,
        )
    return MetricTypeResponse(
        id=m.code,
        name=m.name,
        unit=m.unit,
        data_type=m.data_type,
        color="#4f46e5",
        icon="monitoring",
        is_system=True,
    )


def _entry_response(e) -> EntryResponse:
    return EntryResponse(
        id=e.id or "",
        metric_code=e.metric_code or "",
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
    metric_svc: MetricDefinitionService = Depends(get_metric_definition_service),
):
    return [_metric_response(m) for m in metric_svc.find_all(uid(current_user))]


@router.post("/metrics", response_model=MetricTypeResponse, status_code=201)
async def api_create_metric(
    data: MetricPreferenceCreate,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricDefinitionService = Depends(get_metric_definition_service),
):
    result = metric_svc.create(data, uid(current_user))
    return _metric_response(result)


@router.get("/metrics/groups", response_model=list[MetricGroupResponse])
async def api_list_metric_groups(
    current_user: User = Depends(get_current_user_or_api),
    group_svc: MetricGroupService = Depends(get_metric_group_service),
):
    return group_svc.get_groups_with_preferences(uid(current_user))


@router.get("/metrics/{metric_id}", response_model=MetricTypeResponse)
async def api_get_metric(
    metric_id: str,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricDefinitionService = Depends(get_metric_definition_service),
):
    result = metric_svc.get(metric_id, uid(current_user))
    return _metric_response(result)


@router.put("/metrics/{metric_id}", response_model=MetricTypeResponse)
async def api_update_metric(
    metric_id: str,
    data: MetricPreferenceCreate,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricDefinitionService = Depends(get_metric_definition_service),
):
    result = metric_svc.update(metric_id, uid(current_user), data)
    return _metric_response(result)


@router.delete("/metrics/{metric_id}", status_code=204)
async def api_delete_metric(
    metric_id: str,
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricDefinitionService = Depends(get_metric_definition_service),
):
    metric_svc.delete(metric_id, uid(current_user))
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Entries
# ---------------------------------------------------------------------------


@router.get("/entries", response_model=EntryListResponse)
async def api_list_entries(
    metric_code: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    current_user: User = Depends(get_current_user_or_api),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    user_id = uid(current_user)
    if not metric_code:
        return EntryListResponse(
            entries=[], total=0, page=page, per_page=per_page, total_pages=1
        )
    entries, total, total_pages = measurement_svc.find_by_metric_type_paginated(
        metric_code, user_id, page=page, per_page=per_page
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
    metric_code: str = Query(...),
    current_user: User = Depends(get_current_user_or_api),
    measurement_svc: MeasurementService = Depends(get_measurement_service),
):
    result = measurement_svc.create(data, metric_code, uid(current_user))
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
