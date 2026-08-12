"""Analytics facade — builds an AnalyticsContext and delegates to strategies."""
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.analytics import (
    AnalyticsOverview,
    CorrelationMatrixResponse,
    ForecastResponse,
    HeatmapResponse,
    TimeSeriesResponse,
    WellnessScoreResponse,
    WorkoutProgressionResponse,
)
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.strategies import (
    AnalyticsContext,
    CorrelationsStrategy,
    ForecastStrategy,
    HeatmapStrategy,
    OverviewStrategy,
    TimeseriesStrategy,
    WellnessScoreStrategy,
    WorkoutProgressionStrategy,
)
from salus.services.analytics.weight import WeightAnalysisService


class AnalyticsService:
    def __init__(
        self,
        uow: IUnitOfWork,
        sleep_svc: SleepAnalysisService,
        activity_svc: ActivityAnalysisService,
        weight_svc: WeightAnalysisService,
        nutrition_svc: NutritionAnalysisService,
    ) -> None:
        self._ctx = AnalyticsContext(
            uow=uow,
            sleep=sleep_svc,
            activity=activity_svc,
            weight=weight_svc,
            nutrition=nutrition_svc,
        )
        self._overview = OverviewStrategy()
        self._timeseries = TimeseriesStrategy()
        self._correlations = CorrelationsStrategy()
        self._forecast = ForecastStrategy()
        self._heatmap = HeatmapStrategy()
        self._wellness = WellnessScoreStrategy()
        self._progression = WorkoutProgressionStrategy()

    def overview(self, user_id: str, range_key: str = "30d") -> AnalyticsOverview:
        return self._overview.compute(self._ctx, user_id, range_key)

    def timeseries(
        self, user_id: str, metric: str, range_key: str = "30d", bucket: str = "daily"
    ) -> TimeSeriesResponse:
        return self._timeseries.compute(self._ctx, user_id, metric, range_key, bucket)

    def correlations(
        self, user_id: str, range_key: str = "90d", min_n: int = 14
    ) -> CorrelationMatrixResponse:
        return self._correlations.compute(self._ctx, user_id, range_key, min_n)

    def forecast(
        self, user_id: str, metric: str, horizon_days: int = 30
    ) -> ForecastResponse:
        return self._forecast.compute(self._ctx, user_id, metric, horizon_days)

    def heatmap(
        self, user_id: str, metric: str, year: int
    ) -> HeatmapResponse:
        return self._heatmap.compute(self._ctx, user_id, metric, year)

    def wellness_score(
        self, user_id: str, date_str: str
    ) -> WellnessScoreResponse:
        return self._wellness.compute(self._ctx, user_id, date_str)

    def workout_progression(
        self, user_id: str, exercise_id: str, range_days: int = 180,
    ) -> WorkoutProgressionResponse | None:
        return self._progression.compute(self._ctx, user_id, exercise_id, range_days)
