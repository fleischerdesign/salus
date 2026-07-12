from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401
    from salus.models import MetricType  # noqa: F401


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


@dataclass
class WidgetContext:
    """Full context for a single dashboard widget, including viz and metadata."""

    widget: "DashboardWidget"
    metric: "MetricType | None"  # type: ignore[name-defined]  # noqa: F821
    viz: WidgetViz


class DashboardWidget(SQLModel, table=True):
    __tablename__ = "dashboard_widget"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    metric_type_id: int = Field(foreign_key="metric_type.id")
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
    metric_type: "MetricType" = Relationship()  # type: ignore[name-defined]  # noqa: F821
