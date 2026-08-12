"""Viz builder strategies for dashboard widgets.

Each strategy builds a :class:`WidgetViz` for one ``source_data_type`` from
the domain analysis services, accessed through the widget service as the
build context (duck-typed ``ctx``).
"""
import json
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from salus.models.dashboard import WidgetViz

if TYPE_CHECKING:
    from salus.services.dashboard_widget import DashboardWidgetService


def delta(
    current: float | None,
    previous: float | None,
    unit: str = "",
    is_integer: bool = False,
    up_is_good: bool = True,
) -> dict[str, object] | None:
    if current is None or previous is None or previous == 0:
        return None
    diff = current - previous
    if is_integer:
        diff_str = f"{abs(diff):.0f}"
    else:
        diff_str = f"{abs(diff):.1f}"
    pct = abs(diff) / abs(previous) * 100
    if unit:
        display = f"{diff_str}{unit}"
    elif diff > 0 and pct >= 1:
        display = f"{pct:.0f}%"
    else:
        display = diff_str
    return {
        "value": diff_str,
        "display": display,
        "direction": "up" if diff > 0 else "down" if diff < 0 else "",
        "positive": (diff > 0 and up_is_good) or (diff < 0 and not up_is_good),
    }


def yesterday(date_str: str) -> str:
    return (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )


def rounded_segments(stages: list[tuple[str, float, str]]) -> list[dict]:
    total = sum(v for _, v, _ in stages)
    if total <= 0:
        return [
            {"label": label, "pct": 0, "css_class": css} for label, _, css in stages
        ]
    raw = [v / total * 100 for _, v, _ in stages]
    pcts = [round(r) for r in raw]
    diff = 100 - sum(pcts)
    if diff != 0:
        fractions = [(raw[i] - pcts[i], i) for i in range(len(stages))]
        fractions.sort(key=lambda x: x[0], reverse=(diff > 0))
        for k in range(abs(diff)):
            pcts[fractions[k % len(fractions)][1]] += 1 if diff > 0 else -1
    return [
        {"label": label, "pct": pcts[i], "css_class": css}
        for i, (label, _, css) in enumerate(stages)
    ]


@runtime_checkable
class VizBuilder(Protocol):
    """Strategy: build a WidgetViz for a specific source_data_type."""

    def build(
        self,
        ctx: "DashboardWidgetService",
        user_id: str,
        target: str,
        color: str,
    ) -> WidgetViz | None: ...


class StepsVizBuilder:
    def build(self, ctx, user_id, target, color):
        trend = ctx._activity.steps_trend(days=1, user_id=user_id, date=target)
        today = trend[-1] if trend else None
        if not today or today.count <= 0:
            return None

        yesterday_trend = ctx._activity.steps_trend(
            days=1, user_id=user_id, date=yesterday(target)
        )
        yesterday_v = yesterday_trend[-1] if yesterday_trend else None

        goal = ctx._resolve_goal(user_id, "steps")
        viz = WidgetViz(
            type="progress",
            title="Steps",
            value=f"{today.count:,}",
            unit="steps",
            subtitle="today",
            color=color,
            delta=delta(
                today.count, yesterday_v.count if yesterday_v else None, is_integer=True
            ),
        )
        if goal is not None:
            compute_progress = ctx._goal.compute_progress(goal)
            viz.goal_label = f"Target: {int(goal.target_value):,} / day"
            viz.goal_percent = compute_progress.percent
            viz.goal_target = float(goal.target_value)
        return viz


class HeartRateVizBuilder:
    def build(self, ctx, user_id, target, color):
        hr = ctx._activity.heart_rate_summary(user_id=user_id, date_str=target)
        if not hr:
            return None

        yesterday_hr = ctx._activity.heart_rate_summary(
            user_id=user_id, date_str=yesterday(target)
        )

        goal = ctx._resolve_goal(user_id, "heart_rate")

        viz = WidgetViz(
            type="pills",
            title="Heart Rate",
            value=f"{hr.resting_bpm:.0f}",
            unit="bpm",
            color=color,
            delta=delta(
                hr.resting_bpm,
                yesterday_hr.resting_bpm if yesterday_hr else None,
                unit=" bpm",
                is_integer=True,
                up_is_good=False,
            ),
            subtitle=f"Min {hr.min_bpm} · Max {hr.max_bpm} · Ø {hr.avg_bpm:.0f}",
        )
        if goal is not None:
            compute_progress = ctx._goal.compute_progress(goal)
            viz.goal_label = f"Target: <{int(goal.target_value)} bpm"
            viz.goal_percent = compute_progress.percent
        return viz


class SleepVizBuilder:
    def build(self, ctx, user_id, target, color):
        sl = ctx._sleep.last_night(user_id=user_id, date_str=target)
        if not sl:
            return None

        yesterday_sleep = ctx._sleep.last_night(
            user_id=user_id, date_str=yesterday(target)
        )
        segments = rounded_segments(
            [
                ("Deep", sl.deep_seconds, "segment-deep"),
                ("REM", sl.rem_seconds, "segment-rem"),
                ("Light", sl.light_seconds, "segment-light"),
                ("Awake", sl.awake_seconds, "segment-awake"),
            ]
        )
        for seg in segments:
            label = seg["label"]
            pct = seg["pct"]
            seg["label"] = f"{label}: {pct:.0f}%"

        return WidgetViz(
            type="bar",
            title="Sleep",
            value=f"{sl.duration_hours:.1f}",
            unit="h",
            color=color,
            delta=delta(
                sl.duration_hours,
                yesterday_sleep.duration_hours if yesterday_sleep else None,
                unit="h",
            ),
            segments=segments,
        )


class NutritionVizBuilder:
    def build(self, ctx, user_id, target, color):
        n = ctx._nutrition.today(user_id=user_id, date_str=target)
        if not n:
            return None

        yesterday_n = ctx._nutrition.today(
            user_id=user_id, date_str=yesterday(target)
        )
        total = n.protein_g + n.carbs_g + n.fat_g
        segments = (
            rounded_segments(
                [
                    ("Protein", n.protein_g, "segment-protein"),
                    ("Carbs", n.carbs_g, "segment-carbs"),
                    ("Fat", n.fat_g, "segment-fat"),
                ]
            )
            if total > 0
            else []
        )
        for seg in segments:
            label = seg["label"]
            if label == "Protein":
                seg["label"] = f"Protein: {n.protein_g:.0f}g"
            elif label == "Carbs":
                seg["label"] = f"Carbs: {n.carbs_g:.0f}g"
            elif label == "Fat":
                seg["label"] = f"Fat: {n.fat_g:.0f}g"

        return WidgetViz(
            type="bar",
            title="Nutrition",
            value=f"{n.total_kcal:.0f}",
            unit="kcal",
            color=color,
            delta=delta(
                n.total_kcal,
                yesterday_n.total_kcal if yesterday_n else None,
                unit=" kcal",
                is_integer=True,
            ),
            segments=segments,
        )


class WeightVizBuilder:
    def build(self, ctx, user_id, target, color):
        w = ctx._weight.current(user_id=user_id, date_str=target)
        if not w:
            return None

        yesterday_w = ctx._weight.current(user_id=user_id, date_str=yesterday(target))
        return WidgetViz(
            type="number",
            title="Weight",
            value=f"{w.weight_kg:.1f}",
            unit="kg",
            color=color,
            delta=delta(
                w.weight_kg,
                yesterday_w.weight_kg if yesterday_w else None,
                unit=" kg",
                up_is_good=False,
            ),
        )


class ExerciseVizBuilder:
    def build(self, ctx, user_id, target, color):
        sessions = ctx._activity.exercise_history(days=7, user_id=user_id, limit=5)
        target_sessions = [s for s in sessions if s.date == target]
        if not target_sessions:
            return None

        total_min = sum(s.duration_seconds for s in target_sessions) / 60
        names = set(s.type_name for s in target_sessions)
        return WidgetViz(
            type="number",
            title="Exercise",
            value=f"{total_min:.0f}",
            unit="min",
            subtitle=", ".join(names),
            color=color,
        )


class GenericVizBuilder:
    """Fallback builder for metric types without a dedicated builder.

    Shows the latest measurement value as a simple number widget.
    """

    def __init__(self, title: str, unit: str, metric_code: str | None) -> None:
        self._title = title
        self._unit = unit
        self._metric_code = metric_code

    def build(self, ctx, user_id, target, color):
        if self._metric_code is None:
            return None
        latest = ctx.uow.measurements.get_latest_by_metric_type(
            metric_code=self._metric_code,
            user_id=user_id,
        )
        if latest is None:
            return None

        if latest.value_numeric is not None:
            value = f"{latest.value_numeric:.1f}" if latest.value_numeric % 1 else f"{latest.value_numeric:.0f}"
        elif latest.value_text is not None:
            value = latest.value_text
        elif latest.value_json is not None:
            try:
                j = json.loads(latest.value_json)
                value = str(j) if not isinstance(j, dict) else next(
                    (str(v) for v in j.values()), "—"
                )
            except Exception:
                value = latest.value_json
        else:
            value = "—"

        return WidgetViz(
            type="number",
            title=self._title,
            value=value,
            unit=self._unit or None,
            color=color,
        )


class BloodPressureVizBuilder:
    def build(self, ctx, user_id, target, color):
        points = ctx._blood_pressure.trend(days=30, user_id=user_id)
        if not points:
            return None

        recent = points[-14:]
        labels = [p.date[-5:] for p in recent]
        systolic_data = [round(p.systolic, 1) for p in recent]
        diastolic_data = [round(p.diastolic, 1) for p in recent]

        latest = points[-1]

        series = [
            {
                "label": "Systolic",
                "data": systolic_data,
                "color": "#ef4444",
                "yAxis": "left",
            },
            {
                "label": "Diastolic",
                "data": diastolic_data,
                "color": "#3b82f6",
                "yAxis": "left",
            },
        ]

        return WidgetViz(
            type="line_chart",
            title="Blood Pressure",
            value=f"{latest.systolic:.0f} / {latest.diastolic:.0f}",
            unit="mmHg",
            color=color,
            labels=labels,
            series=series,
        )


VIZ_BUILDERS: dict[str, VizBuilder] = {
    "steps": StepsVizBuilder(),
    "heart_rate": HeartRateVizBuilder(),
    "sleep": SleepVizBuilder(),
    "nutrition": NutritionVizBuilder(),
    "weight": WeightVizBuilder(),
    "exercise": ExerciseVizBuilder(),
    "blood_pressure": BloodPressureVizBuilder(),
}
