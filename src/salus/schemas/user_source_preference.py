from datetime import datetime
from pydantic import BaseModel, Field


class UserSourcePreferenceCreate(BaseModel):
    metric_code: str
    source: str
    priority_rank: int = Field(default=1, ge=1)
    is_enabled: bool = True


class UserSourcePreferenceUpdate(BaseModel):
    priority_rank: int | None = Field(default=None, ge=1)
    is_enabled: bool | None = None


class UserSourcePreferenceResponse(BaseModel):
    id: str
    user_id: str
    metric_code: str
    source: str
    priority_rank: int
    is_enabled: bool
    created_at: datetime
    updated_at: datetime | None = None


class MetricSourcePriorityItem(BaseModel):
    source: str
    priority_rank: int = Field(default=1, ge=1)
    is_enabled: bool = True


class BulkSourcePriorityUpdate(BaseModel):
    metric_code: str
    priorities: list[MetricSourcePriorityItem]


class MetricSourcePriorityMapResponse(BaseModel):
    metric_code: str
    priorities: list[MetricSourcePriorityItem]
