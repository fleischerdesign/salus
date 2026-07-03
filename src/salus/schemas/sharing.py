from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class PeerMetricInfo(BaseModel):
    metric_name: str
    icon: str = "monitoring"
    color: str = "#4f46e5"
    aggregation: str = "daily_summary"
    direction: str  # "outgoing" or "incoming"
    relationship_id: int


class PeerConnection(BaseModel):
    handle: str
    display_name: str | None = None
    is_mutual: bool = False
    is_remote: bool = False
    is_pending: bool = False
    metrics: list[PeerMetricInfo] = []
    expiration: Optional[datetime] = None
    api_token: Optional[str] = None
