from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401
    from salus.models.metric_definition import MetricDefinition  # noqa: F401


class WidgetSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class WidgetViz:
    """Visualisation payload returned by DashboardWidgetService.widget_data()."""

    type: str
    title: str
    icon: str | None = None
    unit: str | None = None
    value: str | float | None = None
    subtitle: str | None = None
    color: str | None = None
    delta: dict[str, object] | None = None
    goal_label: str | None = None
    goal_percent: float | None = None
    goal_target: float | None = None
    segments: list[dict] | None = None
    empty: bool = False
    empty_text: str | None = None
    trend: list[float] | None = None
    trend_labels: list[str] | None = None
    trend_slope: float | None = None
    trend_r_squared: float | None = None
    trend_direction: str | None = None
    forecast_value: float | None = None
    forecast_lower: float | None = None
    forecast_upper: float | None = None
    sparkline_path: str | None = None
    labels: list[str] | None = None
    series: list[dict] | None = None


@dataclass
class WidgetContext:
    """Full context for a single dashboard widget, including viz and metadata."""

    widget: "DashboardWidget"
    metric: "MetricDefinition | None"  # type: ignore[name-defined]  # noqa: F821
    viz: WidgetViz


class DashboardWidget(SQLModel, table=True):
    __tablename__ = "dashboard_widget"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    widget_type: str = Field(default="metric")
    metric_code: str | None = Field(default=None, foreign_key="metric_definition.code", nullable=True)
    position: int = Field(default=0)
    size: WidgetSize = Field(default=WidgetSize.MEDIUM)
    config_json: str = Field(default="{}")
    is_visible: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    user: "User" = Relationship()  # type: ignore[name-defined]  # noqa: F821
    metric_definition: "MetricDefinition" = Relationship()  # type: ignore[name-defined]  # noqa: F821
