from pydantic import BaseModel

from salus.models import DataType


class MetricTypeResponse(BaseModel):
    id: str
    name: str
    unit: str
    data_type: DataType
    color: str
    icon: str
    is_system: bool


class GroupMetricResponse(BaseModel):
    code: str
    name: str
    unit: str
    data_type: str
    source_data_type: str | None = None
    description: str | None = None
    sort_order: int = 0
    color: str
    icon: str
    widget_size: str
    widget_enabled: bool
    enabled: bool
    position: int


class MetricGroupResponse(BaseModel):
    key: str
    name: str
    icon: str
    description: str | None = None
    input_mode: str
    metrics: list[GroupMetricResponse]
