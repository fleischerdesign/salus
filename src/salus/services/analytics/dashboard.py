from salus.models.analytics import DashboardSummary
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.weight import WeightAnalysisService


class DashboardService:
    def __init__(
        self,
        sleep_svc: SleepAnalysisService,
        activity_svc: ActivityAnalysisService,
        weight_svc: WeightAnalysisService,
        nutrition_svc: NutritionAnalysisService,
    ) -> None:
        self._sleep = sleep_svc
        self._activity = activity_svc
        self._weight = weight_svc
        self._nutrition = nutrition_svc

    def summary(self) -> DashboardSummary:
        steps_list = self._activity.steps_trend(days=1)
        steps = steps_list[0] if steps_list else None
        hr = self._activity.heart_rate_summary()
        sleep = self._sleep.last_night()
        nutrition = self._nutrition.today()
        weight = self._weight.current()

        return DashboardSummary(
            steps=steps,
            steps_goal=10000,
            heart_rate=hr,
            sleep=sleep,
            nutrition=nutrition,
            weight=weight,
        )
