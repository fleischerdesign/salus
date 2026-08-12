"""Dashboard overview aggregation strategy."""
from salus.schemas.analytics import (
    AnalyticsExerciseSession,
    AnalyticsOverview,
    AnalyticsSleepSummary,
    AnalyticsTdeeData,
    AnalyticsWeightPoint,
    AnalyticsWeightTrend,
)
from salus.services.analytics.strategies._helpers import compute_tdee
from salus.services.analytics.strategies.context import AnalyticsContext

RANGE_DAYS: dict[str, int] = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}


class OverviewStrategy:
    def compute(
        self, ctx: AnalyticsContext, user_id: str, range_key: str = "30d"
    ) -> AnalyticsOverview:
        days = RANGE_DAYS.get(range_key, 30)

        steps = ctx.activity.steps_trend(days=days, user_id=user_id)
        sleep_list = ctx.sleep.trend(days=days, user_id=user_id)
        weight_trend = ctx.weight.trend(days=days, user_id=user_id)
        exercise_sessions = ctx.activity.exercise_history(
            days=days, user_id=user_id, limit=5
        )
        tdee = compute_tdee(ctx, user_id=user_id, weight_trend=weight_trend)

        return AnalyticsOverview(
            steps_points=[
                {"date": s.date, "count": s.count} for s in steps
            ],
            weight_points=[
                {"date": w.date, "weight_kg": round(w.weight_kg, 1)}
                for w in weight_trend.points
            ],
            sleep_summaries=[
                AnalyticsSleepSummary(
                    date=s.date,
                    duration_hours=round(s.duration_hours, 2),
                    awake_pct=round(s.awake_pct, 1),
                    light_pct=round(s.light_pct, 1),
                    deep_pct=round(s.deep_pct, 1),
                    rem_pct=round(s.rem_pct, 1),
                )
                for s in sleep_list
            ],
            latest_sleep=(
                AnalyticsSleepSummary(
                    date=sleep_list[-1].date,
                    duration_hours=round(sleep_list[-1].duration_hours, 2),
                    awake_pct=round(sleep_list[-1].awake_pct, 1),
                    light_pct=round(sleep_list[-1].light_pct, 1),
                    deep_pct=round(sleep_list[-1].deep_pct, 1),
                    rem_pct=round(sleep_list[-1].rem_pct, 1),
                )
                if sleep_list
                else None
            ),
            weight_trend=AnalyticsWeightTrend(
                points=[
                    AnalyticsWeightPoint(
                        date=p.date, weight_kg=round(p.weight_kg, 1)
                    )
                    for p in weight_trend.points
                ],
                current=weight_trend.current,
                start=weight_trend.start,
                delta=weight_trend.delta,
            ),
            tdee=(
                AnalyticsTdeeData(
                    tdee_kcal=tdee.tdee_kcal,
                    bmr_kcal=tdee.bmr_kcal,
                    pal_factor=tdee.pal_factor,
                    hrr_pct=tdee.hrr_pct,
                )
                if tdee
                else None
            ),
            exercise_sessions=[
                AnalyticsExerciseSession(
                    type_name=s.type_name if s else "",
                    date=s.date if s else "",
                    time=s.time if s else "",
                    duration_seconds=s.duration_seconds if s else 0,
                    distance_meters=s.distance_meters if s else 0,
                    calories=s.calories if s else 0,
                )
                for s in exercise_sessions
            ],
            days=days,
            range_key=range_key,
        )
