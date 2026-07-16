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


class AnalyticsOverview(BaseModel):
    steps_points: list[dict[str, object]]
    weight_points: list[dict[str, object]]
    sleep_summaries: list[AnalyticsSleepSummary]
    latest_sleep: AnalyticsSleepSummary | None
    weight_trend: AnalyticsWeightTrend
    tdee: AnalyticsTdeeData | None
    exercise_sessions: list[AnalyticsExerciseSession]
    days: int
    range_key: str


class TimeSeriesPoint(BaseModel):
    date: str
    value: float
    ci_lower: float | None = None
    ci_upper: float | None = None


class TimeSeriesResponse(BaseModel):
    metric: str
    points: list[TimeSeriesPoint]
    n: int
    bucket: str
    range_key: str


class CorrelationModel(BaseModel):
    metric_a: str
    metric_b: str
    pearson_r: float
    pearson_p: float
    spearman_r: float
    spearman_p: float
    p_adjusted_bh: float
    effect_size_d: float
    ci_95_lower: float
    ci_95_upper: float
    n: int
    interpretation: str


class CorrelationMatrixResponse(BaseModel):
    pairs: list[CorrelationModel]
    n_comparisons: int
    correction: str
    min_n: int
    range_key: str


class ForecastPoint(BaseModel):
    date: str
    predicted: float
    ci_lower: float
    ci_upper: float


class ForecastResponse(BaseModel):
    metric: str
    points: list[ForecastPoint]
    method: str
    r_squared: float
    mape: float | None
    n_train: int
    horizon_days: int


class HeatmapDay(BaseModel):
    date: str
    value: float | None
    percentile_rank: float | None


class HeatmapResponse(BaseModel):
    metric: str
    year: int
    days: list[HeatmapDay]
    max_value: float | None
    method: str


class WellnessComponent(BaseModel):
    z_score: float
    raw_value: float


class WellnessScoreResponse(BaseModel):
    date: str
    score: float
    interpretation: str
    sleep: WellnessComponent
    hrv: WellnessComponent
    resting_hr: WellnessComponent
    steps: WellnessComponent
    n_baseline_days: int


class MethodologyEntry(BaseModel):
    name: str
    description: str
    doi: str | None
    citation: str
    invariants: list[str]


class MethodologyIndexResponse(BaseModel):
    methods: list[MethodologyEntry]


class WorkoutSet(BaseModel):
    weight: float
    reps: float


class WorkoutSessionItem(BaseModel):
    date: str
    total_tonnage: float
    max_weight: float
    sets_count: int


class OneRMResultModel(BaseModel):
    one_rm: float
    ci_lower: float
    ci_upper: float
    n_sets: int
    r_squared: float


class WorkoutProgressionResponse(BaseModel):
    exercise_name: str
    sessions: list[WorkoutSessionItem]
    one_rm: OneRMResultModel
    slope_kg_per_week: float
    r_squared: float
    is_plateaued: bool


class AnalyticsComputeRequest(BaseModel):
    metric: str
    range: str
    method: str
    params: dict[str, object] | None = None


class AnalyticsComputeResponse(BaseModel):
    result: object


class InsightResponse(BaseModel):
    id: str
    date: str
    content: str
    model_used: str


class InsightHistoryItem(BaseModel):
    id: str
    date: str
    model_used: str
    preview: str


class InsightHistoryResponse(BaseModel):
    items: list[InsightHistoryItem]
    total: int
