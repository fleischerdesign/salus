from pydantic import BaseModel

from salus.models import DataType


class MetricTypeCreate(BaseModel):
    name: str
    unit: str = ""
    data_type: DataType = DataType.NUMBER
    color: str = "#4f46e5"
    icon: str = "monitoring"
