from pydantic import BaseModel

from salus.models import DataType
from salus.services._helpers import DEFAULT_METRIC_COLOR


class MetricTypeCreate(BaseModel):
    name: str
    unit: str = ""
    data_type: DataType = DataType.NUMBER
    color: str = DEFAULT_METRIC_COLOR
    icon: str = "monitoring"
