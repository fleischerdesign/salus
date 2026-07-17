import json
import logging
from datetime import datetime, timedelta
from typing import Protocol, runtime_checkable

from salus.models.dashboard import DashboardWidget, WidgetSize, WidgetViz
from salus.models.goal import Goal
from salus.models.metric_definition import MetricDefinition
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.stats import (
    linear_regression,
    mann_kendall,
    prediction_interval,
)
from salus.services.analytics.weight import WeightAnalysisService
from salus.services.analytics.blood_pressure import BloodPressureAnalysisService
from salus.services.goal import GoalService

logger = logging.getLogger(__name__)

EMPTY_TEXTS: dict[str, str] = {
    "steps": "No step data yet. Connect a health source to get started.",
    "heart_rate": "No heart rate data synced yet.",
    "sleep": "No sleep data recorded yet.",
    "weight": "No weight data recorded yet.",
    "nutrition": "No nutrition data logged yet.",
    "exercise": "No exercise data synced yet.",
    "blood_pressure": "No blood pressure data.",
    "blood_glucose": "No blood glucose data.",
    "body_fat": "No body fat data.",
    "water": "No water intake logged.",
    "stress": "No stress data.",
    "readiness": "No readiness data.",
}

VIZ_TYPE_DEFAULTS: dict[str, str] = {
    "steps": "progress",
    "heart_rate": "pills",
    "sleep": "bar",
    "weight": "number",
    "nutrition": "bar",
    "exercise": "number",
    "blood_pressure": "line_chart",
}


# ---------------------------------------------------------------------------
#  Free functions (pure helpers, no state)
# ---------------------------------------------------------------------------


def _delta(
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


def _yesterday(date_str: str) -> str:
    return (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )


def _rounded_segments(stages: list[tuple[str, float, str]]) -> list[dict]:
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


def _enrich_with_trend(
    viz: WidgetViz,
    daily_values: list[float],
    daily_labels: list[str],
) -> WidgetViz:
    if len(daily_values) < 5:
        return viz
    xs = [float(i) for i in range(len(daily_values))]
    reg = linear_regression(xs, daily_values)
    mk = mann_kendall(daily_values)
    if reg:
        viz.trend_slope = round(reg.slope, 4)
        viz.trend_r_squared = round(reg.r_squared, 4)
        pi = prediction_interval(reg, float(len(xs)), confidence=0.80)
        if pi:
            viz.forecast_value = round(pi.point_estimate, 2)
            viz.forecast_lower = round(pi.lower, 2)
            viz.forecast_upper = round(pi.upper, 2)
    if mk:
        viz.trend_direction = mk.trend
    viz.trend = [round(v, 2) for v in daily_values[-7:]]
    viz.trend_labels = daily_labels[-7:]
    recent = daily_values[-7:]
    if len(recent) >= 2:
        mn = min(recent)
        mx = max(recent) - mn or 1.0
        points = []
        for i, v in enumerate(recent):
            x = i * (100.0 / max(len(recent) - 1, 1))
            y = 60.0 - (v - mn) / mx * 50.0
            points.append(f"{x:.2f},{y:.2f}")
        viz.sparkline_path = " ".join(points)
    return viz


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
            days=1, user_id=user_id, date=_yesterday(target)
        )
        yesterday = yesterday_trend[-1] if yesterday_trend else None

        goal = ctx._resolve_goal(user_id, "steps")
        viz = WidgetViz(
            type="progress",
            title="Steps",
            value=f"{today.count:,}",
            unit="steps",
            subtitle="today",
            color=color,
            delta=_delta(
                today.count, yesterday.count if yesterday else None, is_integer=True
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
            user_id=user_id, date_str=_yesterday(target)
        )

        goal = ctx._resolve_goal(user_id, "heart_rate")

        viz = WidgetViz(
            type="pills",
            title="Heart Rate",
            value=f"{hr.resting_bpm:.0f}",
            unit="bpm",
            color=color,
            delta=_delta(
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
            user_id=user_id, date_str=_yesterday(target)
        )
        segments = _rounded_segments(
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
            delta=_delta(
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
            user_id=user_id, date_str=_yesterday(target)
        )
        total = n.protein_g + n.carbs_g + n.fat_g
        segments = (
            _rounded_segments(
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
            delta=_delta(
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

        yesterday_w = ctx._weight.current(user_id=user_id, date_str=_yesterday(target))
        return WidgetViz(
            type="number",
            title="Weight",
            value=f"{w.weight_kg:.1f}",
            unit="kg",
            color=color,
            delta=_delta(
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

    def __init__(self, title: str, unit: str) -> None:
        self._title = title
        self._unit = unit

    def build(self, ctx, user_id, target, color):
        latest = ctx.uow.measurements.get_latest_by_metric_type(
            metric_code=ctx._current_metric_id,
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


_VIZ_BUILDERS: dict[str, VizBuilder] = {
    "steps": StepsVizBuilder(),
    "heart_rate": HeartRateVizBuilder(),
    "sleep": SleepVizBuilder(),
    "nutrition": NutritionVizBuilder(),
    "weight": WeightVizBuilder(),
    "exercise": ExerciseVizBuilder(),
    "blood_pressure": BloodPressureVizBuilder(),
}


# ---------------------------------------------------------------------------
#  Service
# ---------------------------------------------------------------------------

class DashboardWidgetService:
    def __init__(
        self,
        uow: IUnitOfWork,
        activity_svc: ActivityAnalysisService,
        sleep_svc: SleepAnalysisService,
        nutrition_svc: NutritionAnalysisService,
        weight_svc: WeightAnalysisService,
        goal_svc: GoalService,
        bp_svc: BloodPressureAnalysisService,
    ) -> None:
        self.uow = uow
        self._activity = activity_svc
        self._sleep = sleep_svc
        self._nutrition = nutrition_svc
        self._weight = weight_svc
        self._goal = goal_svc
        self._blood_pressure = bp_svc

        # Request-level caches to optimize N+1 query patterns
        self._goals_cache: list[Goal] | None = None
        self._metrics_cache: dict[str, MetricDefinition] = {}

        # Set per-widget during widget_data() for GenericVizBuilder access
        self._current_metric_id: str | None = None

    def ensure_defaults(self, user_id: str) -> list[DashboardWidget]:
        existing = self.uow.dashboard_widgets.find_by_user(user_id)
        if existing:
            return existing
        prefs = self.uow.metric_preferences.find_all(user_id)
        enabled_prefs = [p for p in prefs if p.widget_enabled]
        widgets: list[DashboardWidget] = []
        for pos, pref in enumerate(enabled_prefs):
            md = self.uow.metric_definitions.find_by_code(pref.metric_code)
            if md is None:
                continue
            viz_type = VIZ_TYPE_DEFAULTS.get(md.source_data_type or "", "number")
            config = json.dumps({"viz_type": viz_type})
            w = DashboardWidget(
                user_id=user_id,
                metric_code=pref.metric_code,
                position=pos,
                size=WidgetSize(pref.widget_size),
                config_json=config,
            )
            self.uow.dashboard_widgets.create(w)
            widgets.append(w)
        return widgets

    def list_widgets(self, user_id: str) -> list[DashboardWidget]:
        return self.uow.dashboard_widgets.find_by_user(user_id)

    def get_widget(self, widget_id: str, user_id: str) -> DashboardWidget:
        w = self.uow.dashboard_widgets.get_by_id(widget_id)
        if w is None or w.user_id != user_id:
            raise ValueError("Widget not found")
        return w

    def add_widget(
        self, user_id: str, widget_type: str, metric_code: str | None, size: WidgetSize
    ) -> DashboardWidget:
        existing = self.uow.dashboard_widgets.find_by_user(user_id)
        position = len(existing)
        
        if widget_type == "metric" and metric_code:
            metric = self.uow.metric_definitions.find_by_code(metric_code)
            viz_type = (
                VIZ_TYPE_DEFAULTS.get(metric.source_data_type or "", "number")
                if metric
                else "number"
            )
            config = json.dumps({"viz_type": viz_type})
        else:
            config = "{}"

        w = DashboardWidget(
            user_id=user_id,
            widget_type=widget_type,
            metric_code=metric_code if widget_type == "metric" else None,
            position=position,
            size=size,
            config_json=config,
        )
        return self.uow.dashboard_widgets.create(w)

    def update_widget(
        self, widget_id: str, user_id: str, size: WidgetSize
    ) -> DashboardWidget:
        w = self.get_widget(widget_id, user_id)
        w.size = size
        return self.uow.dashboard_widgets.update(w)

    def delete_widget(self, widget_id: str, user_id: str) -> None:
        w = self.get_widget(widget_id, user_id)
        self.uow.dashboard_widgets.delete(w)

    def reorder(self, user_id: str, ordered_ids: list[str]) -> None:
        self.uow.dashboard_widgets.reorder(user_id, ordered_ids)

    def widget_data(
        self, widget: DashboardWidget, user_id: str, date: str | None = None
    ) -> WidgetViz:
        """Build a WidgetViz for a single widget.

        Always returns a WidgetViz with at least ``title`` and ``type``
        set — even when no data exists (``empty=True``).
        """
        if widget.widget_type != "metric" or not widget.metric_code:
            if widget.widget_type == "workout_launcher":
                return WidgetViz(
                    type="workout_launcher",
                    title="Workout Launcher",
                    empty=False,
                    value=""
                )
            if widget.widget_type == "sleep_coach":
                return WidgetViz(
                    type="sleep_coach",
                    title="Sleep Coach",
                    empty=False,
                    value=""
                )
            return WidgetViz(
                type="number",
                title="Custom Widget",
                empty=True,
                empty_text="Custom widget layout",
            )

        metric = self.uow.metric_definitions.find_by_code(widget.metric_code)
        if metric is None:
            return WidgetViz(
                type="number",
                title=f"Metric #{widget.metric_code}",
                empty=True,
                empty_text="Unknown metric",
            )

        pref = self.uow.metric_preferences.find_by_user_and_code(user_id, widget.metric_code) if widget.metric_code else None
        metric_color = pref.color if pref else "#64748b"
        metric_icon = pref.icon if pref else "monitoring"

        sd = metric.source_data_type
        today_str = datetime.today().strftime("%Y-%m-%d")
        target = date if date else today_str

        try:
            config = json.loads(widget.config_json)
        except (json.JSONDecodeError, TypeError):
            config = {}
        viz_type = config.get("viz_type") or VIZ_TYPE_DEFAULTS.get(sd or "", "number")

        builder = _VIZ_BUILDERS.get(sd or "")
        if builder is None:
            builder = GenericVizBuilder(title=metric.name, unit=metric.unit)
            self._current_metric_id = widget.metric_code

        try:
            viz = builder.build(self, user_id=user_id, target=target, color=metric_color)
        except Exception:
            logger.exception("Error building viz for widget %s (sd=%s)", widget.id, sd)
            viz = None

        self._current_metric_id = None

        if viz is None:
            return WidgetViz(
                type=viz_type,
                title=metric.name,
                icon=metric_icon,
                color=metric_color,
                empty=True,
                empty_text=EMPTY_TEXTS.get(sd or "", "No data recorded yet."),
            )

        # Override viz type with configured type (allows user to change display)
        viz.type = viz_type
        viz.icon = metric_icon
        viz.color = metric_color or viz.color
        return viz

    # ------------------------------------------------------------------
    #  Helpers used by VizBuilder strategies
    # ------------------------------------------------------------------

    def _resolve_goal(self, user_id: str, source_data_type: str) -> Goal | None:
        if self._goals_cache is None:
            self._goals_cache = self._goal.find_all(user_id)
        if not self._metrics_cache:
            for md in self.uow.metric_definitions.find_all():
                self._metrics_cache[md.code] = md

        daily_goals: list[Goal] = []
        for g in self._goals_cache:
            if g.frequency.value != "daily":
                continue
            mt = self._metrics_cache.get(g.metric_code)
            if mt and mt.source_data_type == source_data_type:
                daily_goals.append(g)
        daily_goals.sort(key=lambda g: g.created_at, reverse=True)
        return daily_goals[0] if daily_goals else None
