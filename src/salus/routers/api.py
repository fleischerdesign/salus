
from fastapi import APIRouter, Depends

from salus.dependencies import (
    get_current_user_or_api,
    get_metric_definition_service,
    get_metric_group_service,
)
from salus.models import DataType
from salus.models.user import User
from salus.schemas.api import MetricGroupResponse, MetricTypeResponse
from salus.services._helpers import uid
from salus.services.metric_definition import MetricDefinitionService
from salus.services.metric_group import MetricGroupService

router = APIRouter(prefix="/api/v1")


def _metric_response(m) -> MetricTypeResponse:
    from salus.models.metric_preference import UserMetricPreference

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


# ── Metrics (read-only reference view) ──


@router.get("/metrics", response_model=list[MetricTypeResponse])
async def api_list_metrics(
    current_user: User = Depends(get_current_user_or_api),
    metric_svc: MetricDefinitionService = Depends(get_metric_definition_service),
):
    return [_metric_response(m) for m in metric_svc.find_all(uid(current_user))]


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
