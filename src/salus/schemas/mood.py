from datetime import date

from pydantic import BaseModel, Field


class MoodTagResponse(BaseModel):
    code: str
    label: str
    emoji: str | None = None
    category: str


class MoodEntryCreate(BaseModel):
    entry_date: date | None = None
    mood_score: int = Field(ge=1, le=10)
    energy_level: int | None = Field(default=None, ge=1, le=10)
    stress_level: int | None = Field(default=None, ge=1, le=10)
    tag_codes: list[str] | None = None
    notes: str | None = None


class MoodEntryResponse(BaseModel):
    id: str
    entry_date: str
    mood_score: int
    energy_level: int | None = None
    stress_level: int | None = None
    tag_codes: list[str] | None = None
    notes: str | None = None
    created_at: str


class MoodStatsResponse(BaseModel):
    average: float
    mode: int | None = None
    trend_slope: float | None = None
    min_score: int
    max_score: int
    total_entries: int
    current_streak: int
    longest_streak: int
    distribution: dict[str, int]
