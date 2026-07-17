
from pydantic import BaseModel, Field

from salus.models.habit import HabitFrequency


class HabitCreate(BaseModel):
    name: str
    description: str | None = None
    color: str = Field(default="#4f46e5")
    icon: str = Field(default="check-circle")
    frequency: HabitFrequency = Field(default=HabitFrequency.DAILY)
    target_count: int = Field(default=1)
    days_bitmask: int | None = None
    stack_hint: str | None = None


class HabitUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    icon: str | None = None
    frequency: HabitFrequency | None = None
    target_count: int | None = None
    days_bitmask: int | None = None
    stack_hint: str | None = None
    is_archived: bool | None = None


class HabitResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    color: str
    icon: str
    frequency: str
    target_count: int
    days_bitmask: int | None = None
    stack_hint: str | None = None
    is_archived: bool
    created_at: str
    current_streak: int = 0
    longest_streak: int = 0
    completion_rate: float = 0.0
    today_completed: bool = False


class HabitLogResponse(BaseModel):
    id: str
    habit_id: str
    log_date: str
    completed: bool
    completed_at: str | None = None
    notes: str | None = None


class HabitCheckResponse(BaseModel):
    completed: bool
    current_streak: int
    longest_streak: int
    completion_rate: float


class HabitStatsResponse(BaseModel):
    current_streak: int
    longest_streak: int
    completion_rate: float
    total_checks: int
    dates: list[str]
