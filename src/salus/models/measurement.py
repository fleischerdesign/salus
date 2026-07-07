from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from salus.models import MetricType  # noqa: F401
    from salus.models.user import User  # noqa: F401


class Measurement(SQLModel, table=True):
    __tablename__ = "measurement"  # pyright: ignore[reportAssignmentType]

    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    metric_type_id: int | None = Field(default=None, foreign_key="metric_type.id")
    data_type: str = Field(default="", index=True)
    source: str = Field(default="manual")
    value_numeric: float | None = Field(default=None)
    value_text: str | None = Field(default=None)
    value_json: str | None = Field(default=None)
    start_time: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), index=True
    )
    end_time: datetime | None = Field(default=None)
    notes: str | None = Field(default=None)
    external_id: str | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="measurements")
    metric_type: "MetricType" = Relationship(back_populates="measurements")  # pyright: ignore[reportAssignmentType]

    @property
    def display_value(self) -> str:
        if self.value_text is not None:
            return self.value_text
        if self.value_numeric is not None:
            return str(self.value_numeric)
        if self.value_json is not None:
            import json
            try:
                data = json.loads(self.value_json)
                if isinstance(data, dict):
                    if "duration_seconds" in data:
                        secs = data["duration_seconds"]
                        hours = secs // 3600
                        mins = (secs % 3600) // 60
                        if hours > 0:
                            return f"{hours}h {mins}m"
                        return f"{mins}m"
                    elif "total_kcal" in data:
                        kcal = data["total_kcal"]
                        p = data.get("protein_g", 0)
                        c = data.get("carbs_g", 0)
                        f = data.get("fat_g", 0)
                        return f"{kcal} kcal ({p}g P, {c}g C, {f}g F)"
            except Exception:
                pass
            return self.value_json
        return ""
