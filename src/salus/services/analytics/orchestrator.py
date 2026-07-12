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
        exercise_sessions = self._activity.exercise_history(
            days=days, user_id=user_id, limit=5
        )

        tdee = self._compute_tdee(user_id=user_id, weight_trend=weight_trend)

        steps_labels = [s.date[-5:] for s in steps]
        steps_data = [s.count for s in steps]
        weight_labels = [w.date[-5:] for w in weight_trend.points]
        weight_data = [round(w.weight_kg, 1) for w in weight_trend.points]

        return {
            "steps_labels": steps_labels,
            "steps_data": steps_data,
            "weight_labels": weight_labels,
            "weight_data": weight_data,
            "sleep_list": [
                {
                    "date": s.date,
                    "duration_hours": round(s.duration_hours, 2),
                    "awake_pct": round(s.awake_pct, 1),
                    "light_pct": round(s.light_pct, 1),
                    "deep_pct": round(s.deep_pct, 1),
                    "rem_pct": round(s.rem_pct, 1),
                }
                for s in sleep_list
            ],
            "latest_sleep": (
                {
                    "date": sleep_list[-1].date,
                    "duration_hours": round(sleep_list[-1].duration_hours, 2),
                    "awake_pct": round(sleep_list[-1].awake_pct, 1),
                    "light_pct": round(sleep_list[-1].light_pct, 1),
                    "deep_pct": round(sleep_list[-1].deep_pct, 1),
                    "rem_pct": round(sleep_list[-1].rem_pct, 1),
                }
                if sleep_list
                else None
            ),
            "weight_trend": {
                "points": [
                    {"date": p.date, "weight_kg": round(p.weight_kg, 1)}
                    for p in weight_trend.points
                ],
                "current": weight_trend.current,
                "start": weight_trend.start,
                "delta": weight_trend.delta,
            },
            "tdee": (
                {
                    "tdee_kcal": tdee.tdee_kcal,
                    "bmr_kcal": tdee.bmr_kcal,
                    "pal_factor": tdee.pal_factor,
                    "hrr_pct": tdee.hrr_pct,
                }
                if tdee
                else None
            ),
            "exercise_sessions": [
                {
                    "type_name": s.type_name,
                    "date": s.date,
                    "time": s.time,
                    "duration_seconds": s.duration_seconds,
                    "distance_meters": s.distance_meters,
                    "calories": s.calories,
                }
                for s in exercise_sessions
            ],
            "days": days,
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
