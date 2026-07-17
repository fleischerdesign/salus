from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class MedicationForm(str, Enum):
    TABLET = "tablet"
    CAPSULE = "capsule"
    LIQUID = "liquid"
    INJECTION = "injection"
    PATCH = "patch"
    CREAM = "cream"
    DROPS = "drops"


class Medication(SQLModel, table=True):
    __tablename__ = "medication"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    name: str
    active_ingredient: str | None = Field(default=None)
    strength: str | None = Field(default=None)
    form: MedicationForm = Field(default=MedicationForm.TABLET)
    instructions: str | None = Field(default=None)
    color_hex: str = Field(default="#4f46e5")
    icon: str = Field(default="medication")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    user: "User" = Relationship()


class MedicationSchedule(SQLModel, table=True):
    __tablename__ = "medication_schedule"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    medication_id: str = Field(foreign_key="medication.id")
    user_id: str = Field(foreign_key="user.id")
    dosage: str
    times: list[str] = Field(sa_column=Column(JSON))
    days_of_week: list[int] | None = Field(default=None, sa_column=Column(JSON))
    start_date: date
    end_date: date | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = Field(default=None)

    medication: "Medication" = Relationship()


class MedicationLog(SQLModel, table=True):
    __tablename__ = "medication_log"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    medication_id: str = Field(foreign_key="medication.id")
    user_id: str = Field(foreign_key="user.id")
    schedule_id: str | None = Field(default=None, foreign_key="medication_schedule.id")
    taken_at: datetime | None = Field(default=None)
    dosage_taken: str | None = Field(default=None)
    skipped: bool = Field(default=False)
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = Field(default=None)

    medication: "Medication" = Relationship()


class MedicationInventory(SQLModel, table=True):
    __tablename__ = "medication_inventory"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    medication_id: str = Field(foreign_key="medication.id", unique=True)
    user_id: str = Field(foreign_key="user.id")
    initial_count: int
    remaining_count: int
    refill_at_count: int
    prescription_refills: int | None = Field(default=None)
    next_refill_date: date | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    medication: "Medication" = Relationship()
