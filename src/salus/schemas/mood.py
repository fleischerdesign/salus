from pydantic import BaseModel


class MoodTagResponse(BaseModel):
    code: str
    label: str
    emoji: str | None = None
    category: str


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
