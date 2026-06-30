from datetime import datetime

from pydantic import BaseModel

from salus.models import DataType


class MetricTypeResponse(BaseModel):
    id: int
    name: str
    unit: str
    data_type: DataType
    color: str


class EntryResponse(BaseModel):
    id: int
    metric_type_id: int
    value: str
    timestamp: datetime
    notes: str | None


class HealthRecordResponse(BaseModel):
    id: str
    data_type: str
    start_time: str
    end_time: str
    value: str
