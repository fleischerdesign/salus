from pydantic import BaseModel


class AnalyticsTdeeData(BaseModel):
    tdee_kcal: float
    bmr_kcal: float
    pal_factor: float
    hrr_pct: float


class AnalyticsWeightPoint(BaseModel):
    date: str
    weight_kg: float


class AnalyticsWeightTrend(BaseModel):
    points: list[AnalyticsWeightPoint]
    current: float | None
    start: float | None
    delta: float | None


class AnalyticsSleepSummary(BaseModel):
    date: str
    duration_hours: float
    awake_pct: float
    light_pct: float
    deep_pct: float
    rem_pct: float


class AnalyticsExerciseSession(BaseModel):
    type_name: str
    date: str
    time: str
    duration_seconds: int
    distance_meters: float
    calories: float


class AnalyticsResponse(BaseModel):
    steps_labels: list[str]
    steps_data: list[int]
    weight_labels: list[str]
    weight_data: list[float]
    sleep_list: list[AnalyticsSleepSummary]
    latest_sleep: AnalyticsSleepSummary | None
    weight_trend: AnalyticsWeightTrend
    tdee: AnalyticsTdeeData | None
    exercise_sessions: list[AnalyticsExerciseSession]
    days: int


class InsightResponse(BaseModel):
    id: int
    date: str
    content: str
    model_used: str


class InsightHistoryItem(BaseModel):
    id: int
    date: str
    model_used: str
    preview: str


class InsightHistoryResponse(BaseModel):
    items: list[InsightHistoryItem]
    total: int
