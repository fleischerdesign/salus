import json

from salus.models.analytics import TDEEResult
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.calculations import (
    calc_bmr_cunningham,
    calc_tef,
    calc_tdee,
)
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.weight import WeightAnalysisService

_RANGE_DAYS: dict[str, int] = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}

_RANGE_BUTTONS = [
    ("7d", "7 Days"),
    ("30d", "30 Days"),
    ("90d", "90 Days"),
    ("1y", "1 Year"),
]


class AnalyticsService:
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

    def build_context(self, user_id: int, range_key: str = "30d") -> dict:
        days = _RANGE_DAYS.get(range_key, 30)

        steps = self._activity.steps_trend(days=days, user_id=user_id)
        sleep_list = self._sleep.trend(days=days, user_id=user_id)
        weight_trend = self._weight.trend(days=days, user_id=user_id)
        nutrition_list = self._nutrition.daily_totals(days=days, user_id=user_id)
        exercise_sessions = self._activity.exercise_history(
            days=days, user_id=user_id, limit=5
        )

        tdee = self._compute_tdee(user_id=user_id, weight_trend=weight_trend)

        steps_labels = [s.date[-5:] for s in steps]
        steps_data = [s.count for s in steps]
        weight_labels = [w.date[-5:] for w in weight_trend.points]
        weight_data = [round(w.weight_kg, 1) for w in weight_trend.points]

        return {
            "steps_labels": json.dumps(steps_labels),
            "steps_data": json.dumps(steps_data),
            "weight_labels": json.dumps(weight_labels),
            "weight_data": json.dumps(weight_data),
            "sleep_list": sleep_list,
            "latest_sleep": sleep_list[-1] if sleep_list else None,
            "weight_trend": weight_trend,
            "bmr": tdee.bmr_kcal if tdee else None,
            "tdee_data": (tdee.tdee_kcal, tdee.pal_factor, tdee.hrr_pct)
            if tdee
            else None,
            "exercise_sessions": exercise_sessions,
            "nutrition_list": nutrition_list,
            "days": days,
            "range_buttons": _RANGE_BUTTONS,
        }

    def _compute_tdee(self, user_id: int, weight_trend) -> TDEEResult | None:
        weight_kg = weight_trend.current
        if not weight_kg:
            return None

        bmr = calc_bmr_cunningham(weight_kg)
        hr_summary = self._activity.heart_rate_summary(user_id=user_id)
        hr_rest = hr_summary.resting_bpm if hr_summary else 60.0
        hr_awake = hr_summary.avg_bpm if hr_summary else 75.0

        nutrition_today = self._nutrition.today(user_id=user_id)
        tef = 0.0
        if nutrition_today:
            tef = calc_tef(
                nutrition_today.protein_g,
                nutrition_today.carbs_g,
                nutrition_today.fat_g,
            )

        tdee_data = calc_tdee(bmr, hr_awake, hr_rest, tef=tef)
        if tdee_data is None:
            return None

        tdee_kcal, pal_factor, hrr_pct = tdee_data
        return TDEEResult(
            bmr_kcal=bmr,
            tdee_kcal=tdee_kcal,
            pal_factor=pal_factor,
            hrr_pct=hrr_pct,
            hr_resting=hr_rest,
            hr_awake_avg=hr_awake,
            lean_mass_kg=None,
            body_fat_pct=None,
        )
