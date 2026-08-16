from datetime import datetime

from pydantic import BaseModel


class MeasurementCreate(BaseModel):
    value: str
    timestamp: datetime | None = None
    notes: str | None = None


class HealthMeasurementIn(BaseModel):
    """A measurement pushed by a device health source (bulk replication path)."""

    id: str
    metric_code: str
    source_data_type: str = ""
    source: str
    value_numeric: float | None = None
    value_text: str | None = None
    value_json: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    external_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class HealthPushRequest(BaseModel):
    measurements: list[HealthMeasurementIn]
