from datetime import date, datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class LabMarker(SQLModel, table=True):
    __tablename__ = "lab_marker"  # pyright: ignore[reportAssignmentType]

    code: str = Field(primary_key=True, foreign_key="metric_definition.code")
    category: str = Field(index=True)
    reference_low: float | None = Field(default=None)
    reference_high: float | None = Field(default=None)
    optimal_low: float | None = Field(default=None)
    optimal_high: float | None = Field(default=None)
    description: str | None = Field(default=None)


class LabPanel(SQLModel, table=True):
    __tablename__ = "lab_panel"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str | None = Field(default=None, foreign_key="user.id", index=True)
    collection_date: date = Field(default_factory=date.today)
    lab_name: str | None = Field(default=None)
    fasting: bool = Field(default=False)
    notes: str | None = Field(default=None)
    attachment_path: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)

    results: list["LabResult"] = Relationship(back_populates="panel")


class LabResult(SQLModel, table=True):
    __tablename__ = "lab_result"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    panel_id: str = Field(foreign_key="lab_panel.id", index=True)
    user_id: str | None = Field(default=None, foreign_key="user.id", index=True)
    metric_code: str = Field(foreign_key="metric_definition.code", index=True)
    value: float
    unit: str | None = Field(default=None)
    is_abnormal: bool = Field(default=False)
    reference_low: float | None = Field(default=None)
    reference_high: float | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default=None)
    deleted_at: datetime | None = Field(default=None)

    panel: LabPanel = Relationship(back_populates="results")
