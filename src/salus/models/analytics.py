from dataclasses import dataclass


@dataclass
class WeightPoint:
    date: str
    weight_kg: float


@dataclass
class WeightTrend:
    points: list[WeightPoint]
    current: float | None
    start: float | None
    delta: float | None


@dataclass
class SleepSummary:
    date: str
    duration_seconds: int
    duration_hours: float
    awake_seconds: int
    light_seconds: int
    deep_seconds: int
    rem_seconds: int

    @property
    def awake_pct(self) -> float:
        if self.duration_seconds <= 0:
            return 0
        return self.awake_seconds / self.duration_seconds * 100

    @property
    def light_pct(self) -> float:
        if self.duration_seconds <= 0:
            return 0
        return self.light_seconds / self.duration_seconds * 100

    @property
    def deep_pct(self) -> float:
        if self.duration_seconds <= 0:
            return 0
        return self.deep_seconds / self.duration_seconds * 100

    @property
    def rem_pct(self) -> float:
        if self.duration_seconds <= 0:
            return 0
        return self.rem_seconds / self.duration_seconds * 100


@dataclass
class HRTimelinePoint:
    time: str
    bpm: float


@dataclass
class HROHLC:
    date: str
    label: str
    open_bpm: float
    high_bpm: float
    low_bpm: float
    close_bpm: float
    count: int


@dataclass
class HRSummary:
    date: str
    measurement_count: int
    avg_bpm: float
    resting_bpm: float
    min_bpm: int
    max_bpm: int


@dataclass
class StepDay:
    date: str
    count: int


@dataclass
class ExerciseSession:
    date: str
    time: str
    type_name: str
    duration_seconds: int
    distance_meters: float
    calories: float


@dataclass
class NutritionDay:
    date: str
    total_kcal: float
    protein_g: float
    carbs_g: float
    fat_g: float


@dataclass
class TDEEResult:
    bmr_kcal: float
    tdee_kcal: float
    pal_factor: float
    hrr_pct: float
    hr_resting: float
    hr_awake_avg: float
    lean_mass_kg: float | None
    body_fat_pct: float | None


@dataclass
class GoalProgress:
    goal_id: str
    current_value: float | None
    target_value: float
    percent: int
    status: str  # "fulfilled" | "pending" | "missed"
    is_fulfilled: bool
