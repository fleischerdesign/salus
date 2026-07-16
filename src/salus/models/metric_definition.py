from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.models import DataType

if TYPE_CHECKING:
    from salus.models.measurement import Measurement  # noqa: F401
    from salus.models.metric_preference import UserMetricPreference  # noqa: F401


class MetricGroup(SQLModel, table=True):
    __tablename__ = "metric_group"  # pyright: ignore[reportAssignmentType]

    key: str = Field(primary_key=True)
    name: str
    icon: str = Field(default="monitoring")
    description: str | None = Field(default=None)
    input_mode: str = Field(default="individual")

    definitions: list["MetricDefinition"] = Relationship(back_populates="group")


class MetricDefinition(SQLModel, table=True):
    __tablename__ = "metric_definition"  # pyright: ignore[reportAssignmentType]

    code: str = Field(primary_key=True)
    name: str
    unit: str = Field(default="")
    data_type: DataType = Field(default=DataType.NUMBER)
    source_data_type: str | None = Field(default=None)
    group_key: str | None = Field(default=None, foreign_key="metric_group.key")
    description: str | None = Field(default=None)
    sort_order: int = Field(default=0)

    group: MetricGroup | None = Relationship(back_populates="definitions")
    measurements: list["Measurement"] = Relationship(back_populates="metric_definition")
    preferences: list["UserMetricPreference"] = Relationship(back_populates="metric_definition")
