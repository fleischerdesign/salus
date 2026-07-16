from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Regression:
    slope: float
    intercept: float
    r_squared: float
    standard_error: float
    n: int
    residuals: tuple[float, ...] = field(default_factory=tuple)
    df: int = 0
    x_mean: float = 0.0
    ssx: float = 0.0

    def __post_init__(self) -> None:
        if self.df == 0 and self.n > 2:
            object.__setattr__(self, "df", self.n - 2)


@dataclass(frozen=True, slots=True)
class PI:
    lower: float
    upper: float
    point_estimate: float
    confidence: float


@dataclass(frozen=True, slots=True)
class Correlation:
    r: float
    n: int
    t_statistic: float
    p_value: float
    ci_lower: float
    ci_upper: float
    df: int = 0

    def __post_init__(self) -> None:
        if self.df == 0 and self.n > 2:
            object.__setattr__(self, "df", self.n - 2)


@dataclass(frozen=True, slots=True)
class EffectSize:
    d: float
    hedges_g: float
    ci_lower: float
    ci_upper: float
    n: int
    interpretation: str


@dataclass(frozen=True, slots=True)
class FDR:
    adjusted: tuple[float, ...]
    rejected: tuple[bool, ...]
    alpha: float = 0.05
    method: str = "Benjamini-Hochberg FDR"


@dataclass(frozen=True, slots=True)
class TrendTest:
    s: float
    z: float
    p_value: float
    trend: str
    n: int
    tau: float


@dataclass(frozen=True, slots=True)
class BootstrapCI:
    lower: float
    upper: float
    point_estimate: float
    n_iter: int
    confidence: float
    seed: int


@dataclass(frozen=True, slots=True)
class Forecast:
    point: tuple[float, ...]
    fitted: tuple[float, ...]
    residuals: tuple[float, ...]
    mape: float | None
    alpha: float
    horizon: int = 1
    n_train: int = 0

    def __post_init__(self) -> None:
        if self.n_train == 0:
            object.__setattr__(self, "n_train", len(self.point) - self.horizon)


@dataclass(frozen=True, slots=True)
class EfficiencyResult:
    efficiency: float
    warning: str | None


@dataclass(frozen=True, slots=True)
class SleepDebtResult:
    debt: tuple[float, ...]
    baseline_h: float


@dataclass(frozen=True, slots=True)
class HRV:
    mean_rr: float
    sdnn: float
    rmssd: float
    pnn50: float
    n: int


@dataclass(frozen=True, slots=True)
class RecoveryScore:
    score: float
    interpretation: str
    sleep_z: float
    hrv_z: float
    hr_z: float
    steps_z: float


@dataclass(frozen=True, slots=True)
class OneRMResult:
    one_rm: float
    ci_lower: float
    ci_upper: float
    n_sets: int
    r_squared: float


@dataclass(frozen=True, slots=True)
class Progression:
    slope_kg_per_week: float
    slope_ci: tuple[float, float]
    r_squared: float
    mann_kendall: TrendTest
    is_plateaued: bool


@dataclass(frozen=True, slots=True)
class Fatigue:
    fitness: tuple[float, ...]
    fatigue: tuple[float, ...]
    performance: tuple[float, ...]
