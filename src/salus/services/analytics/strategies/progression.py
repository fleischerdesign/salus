"""Workout progression (tonnage + 1RM) strategy."""
from datetime import datetime, timedelta, timezone

from salus.schemas.analytics import (
    OneRMResultModel,
    WorkoutProgressionResponse,
    WorkoutSessionItem,
)
from salus.services.analytics.stats import one_rm_regression, tonnage_progression
from salus.services.analytics.strategies.context import AnalyticsContext


class WorkoutProgressionStrategy:
    def compute(
        self,
        ctx: AnalyticsContext,
        user_id: str,
        exercise_id: str,
        range_days: int = 180,
    ) -> WorkoutProgressionResponse | None:
        since = datetime.now(timezone.utc) - timedelta(days=range_days)
        repo = ctx.uow.workout_log_entries
        rows = repo.get_exercise_progression(user_id, exercise_id, since=since)
        if not rows:
            return None
        exercise = ctx.uow.exercises.get_by_id(exercise_id)
        exercise_name = exercise.name if exercise else "unknown"
        session_items = [
            WorkoutSessionItem(
                date=str(r["date"]),
                total_tonnage=float(r["total_tonnage"]),
                max_weight=float(r["max_weight"]),
                sets_count=int(r["sets_count"]),
            )
            for r in rows
        ]
        weeks: list[int] = []
        tonnages: list[float] = []
        all_sets: list[tuple[float, float]] = []
        week_idx = 0
        last_week = ""
        for si in session_items:
            iso = si.date[:7]
            if iso != last_week:
                week_idx += 1
                last_week = iso
            weeks.append(week_idx)
            tonnages.append(si.total_tonnage)
            if si.max_weight > 0:
                for _ in range(si.sets_count):
                    all_sets.append((si.max_weight, 5.0))
        session_tonnages = list(zip(weeks, tonnages))
        prog = tonnage_progression(session_tonnages)
        one_rm = one_rm_regression(all_sets)
        if prog is None:
            return None
        return WorkoutProgressionResponse(
            exercise_name=exercise_name,
            sessions=session_items,
            one_rm=OneRMResultModel(
                one_rm=one_rm.one_rm if one_rm else 0.0,
                ci_lower=one_rm.ci_lower if one_rm else 0.0,
                ci_upper=one_rm.ci_upper if one_rm else 0.0,
                n_sets=one_rm.n_sets if one_rm else 0,
                r_squared=round(one_rm.r_squared, 4) if one_rm else 0.0,
            ),
            slope_kg_per_week=round(prog.slope_kg_per_week, 4),
            r_squared=round(prog.r_squared, 4),
            is_plateaued=prog.is_plateaued,
        )
