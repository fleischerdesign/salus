from datetime import datetime

from pydantic import BaseModel


class MeasurementCreate(BaseModel):
    value: str
    timestamp: datetime | None = None
    notes: str | None = None
