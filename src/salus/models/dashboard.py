from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class WidgetSize(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


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
