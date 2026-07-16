from datetime import datetime

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


class EntryResponse(BaseModel):
    id: str
    metric_code: str
    value: str
    timestamp: datetime
    notes: str | None


class EntryUpdate(BaseModel):
    value: str | None = None
    timestamp: datetime | None = None
    notes: str | None = None


class MetricOverviewResponse(BaseModel):
    metric_id: str
    latest_value: str | None
    latest_date: str | None
    entry_count: int


class EntryListResponse(BaseModel):
    entries: list[EntryResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class HealthRecordResponse(BaseModel):
    id: str
    data_type: str
    start_time: str
    end_time: str
    value: str
