from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models.measurement import Measurement  # noqa: F401
    from salus.models.user import User  # noqa: F401


class DataType(str, Enum):
    NUMBER = "number"
    TEXT = "text"
    BOOLEAN = "boolean"


class MetricType(SQLModel, table=True):
    __tablename__ = "metric_type"  # pyright: ignore[reportAssignmentType]
    __table_args__ = (UniqueConstraint("name", "user_id"),)

    id: int | None = Field(default=None, primary_key=True)
    name: str
    unit: str = Field(default="")
    data_type: DataType = Field(default=DataType.NUMBER)
    color: str = Field(default="#4f46e5")
    user_id: int = Field(foreign_key="user.id")
    is_system: bool = Field(default=False)
    source_data_type: str | None = Field(default=None)
    icon: str = Field(default="monitoring")
    widget_size: str = Field(default="medium")
    widget_enabled: bool = Field(default=False)

    user: "User" = Relationship(back_populates="metric_types")
    measurements: list["Measurement"] = Relationship(back_populates="metric_type")