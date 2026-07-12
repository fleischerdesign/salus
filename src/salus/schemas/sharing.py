from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from salus.services._helpers import DEFAULT_METRIC_COLOR


class PeerMetricInfo(BaseModel):
    metric_name: str
    icon: str = "monitoring"
    color: str = DEFAULT_METRIC_COLOR
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
    last_sync: Optional[str] = None  # human-readable, e.g. "2 min ago"
