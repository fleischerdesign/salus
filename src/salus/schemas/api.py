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


class EntryResponse(BaseModel):
    id: str
    metric_type_id: str
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
