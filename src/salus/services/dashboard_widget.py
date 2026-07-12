from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from typing import Protocol, runtime_checkable

from salus.models.analytics import HROHLC, HRTimelinePoint
from salus.models.dashboard import DashboardWidget, WidgetSize, WidgetViz
from salus.models.goal import Goal
from salus.models import MetricType
from salus.repositories.protocols import (
    IDashboardWidgetRepository,
    IMeasurementRepository,
    IMetricTypeRepository,
)
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.weight import WeightAnalysisService
from salus.services.goal import GoalService

logger = logging.getLogger(__name__)

_EMPTY_TEXTS: dict[str, str] = {
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

_VIZ_TYPE_DEFAULTS: dict[str, str] = {
    "steps": "progress",
    "heart_rate": "pills",
    "sleep": "bar",
    "weight": "number",
    "nutrition": "bar",
    "exercise": "number",
}


# ---------------------------------------------------------------------------
#  Free functions (pure helpers, no state)
# ---------------------------------------------------------------------------

def _compute_sparkline(values: list[float]) -> str:
    if not values or max(values) == 0:
        return "0,30 100,30"
    max_val = max(values)
    h = 26
    points = []
    for i, v in enumerate(values):
        x = (i / max(len(values) - 1, 1)) * 100
        y = h - (v / max_val * h)
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


def _delta_str(
    current: float | None,
    previous: float | None,
    unit: str = "",
    is_integer: bool = False,
    up_is_good: bool = True,
) -> str | None:
    if current is None or previous is None or previous == 0:
        return None
    diff = current - previous
    if is_integer:
        diff_str = f"{abs(diff):.0f}"
    else:
        diff_str = f"{abs(diff):.1f}"
    pct = abs(diff) / abs(previous) * 100
    direction = "&#8593;" if diff > 0 else "&#8595;" if diff < 0 else ""
    if up_is_good:
        css_class = "positive" if diff > 0 else "negative" if diff < 0 else ""
    else:
        css_class = "positive" if diff < 0 else "negative" if diff > 0 else ""
    if unit:
        return (
            f'<span class="widget-delta widget-delta--{css_class}">'
            f"{direction} {diff_str}{unit}</span>"
        )
    if diff > 0 and pct >= 1:
        return (
            f'<span class="widget-delta widget-delta--{css_class}">'
            f"{direction} {pct:.0f}%</span>"
        )
    return f'<span class="widget-delta widget-delta--{css_class}">{direction} {diff_str}</span>'


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


def _compute_candlestick_chart(ohlc_list: list[HROHLC], reference_bpm: float) -> dict:
    valid = [c for c in ohlc_list if c.count > 0]
    if not valid:
        return {"empty": True}

    global_min = min(c.low_bpm for c in valid)
    global_max = max(c.high_bpm for c in valid)
    value_range = global_max - global_min
    if value_range < 1:
        value_range = max(global_max * 0.2, 1)

    pad_top = 8
    pad_bottom = 18
    pad_x = 6
    chart_w = 200
    chart_h = 100
    plot_h = chart_h - pad_top - pad_bottom

    n = len(ohlc_list)
    slot_w = (chart_w - 2 * pad_x) / n
    half_w = slot_w * 0.25

    def _scale(val: float) -> float:
        return pad_top + plot_h * (1 - (val - global_min) / value_range)

    candles: list[dict] = []
    for i, c in enumerate(ohlc_list):
        cx = pad_x + slot_w * i + slot_w / 2
        if c.count == 0:
            candles.append({"cx": cx, "label": c.label, "empty": True})
            continue

        high_y = _scale(c.high_bpm)
        low_y = _scale(c.low_bpm)
        open_y = _scale(c.open_bpm)
        close_y = _scale(c.close_bpm)

        body_y = min(open_y, close_y)
        body_h = max(abs(close_y - open_y), 1.5)
        fill = "#22c55e" if c.close_bpm >= c.open_bpm else "#ef4444"

        candles.append(
            {
                "cx": cx,
                "high_y": high_y,
                "low_y": low_y,
                "body_y": body_y,
                "body_h": body_h,
                "half_w": half_w,
                "fill": fill,
                "label": c.label,
                "empty": False,
            }
        )

    return {
        "candles": candles,
        "chart_w": chart_w,
        "chart_h": chart_h,
        "reference_y": _scale(reference_bpm),
        "empty": False,
    }


def _compute_pill_chart(
    timeline: list[HRTimelinePoint],
    resting_bpm: float,
    color: str,
    target_bpm: float | None = None,
) -> dict:
    if not timeline:
        return {"empty": True}

    bpms = [p.bpm for p in timeline]
    y_min = max(0, min(min(bpms) - 10, resting_bpm - 10))
    y_max = max(max(bpms) + 15, resting_bpm + 15)
    if target_bpm is not None and target_bpm > y_max:
        y_max = target_bpm + 5
    if y_max <= y_min:
        y_max = y_min + 20
    y_range = y_max - y_min

    # Group timeline points into 15-minute buckets (96 intervals)
    buckets: dict[int, list[float]] = {i: [] for i in range(96)}
    for p in timeline:
        parts = p.time.split(":")
        m = int(parts[0]) * 60 + int(parts[1])
        bucket_idx = m // 15
        if bucket_idx in buckets:
            buckets[bucket_idx].append(p.bpm)

    pills: list[dict] = []
    for idx in sorted(buckets.keys()):
        bpms_in_bucket = buckets[idx]
        if not bpms_in_bucket:
            continue
        min_b = min(bpms_in_bucket)
        max_b = max(bpms_in_bucket)

        h1 = (idx * 15) // 60
        m1 = (idx * 15) % 60
        h2 = (idx * 15 + 15) // 60
        m2 = (idx * 15 + 15) % 60
        if h2 == 24:
            h2 = 0
        time_str = f"{h1:02d}:{m1:02d} - {h2:02d}:{m2:02d}"

        pills.append(
            {
                "min_bpm": int(min_b),
                "max_bpm": int(max_b),
                "color": color,
                "x_fraction": round((idx * 15) / 1440, 4),
                "tooltip": f"{time_str} &middot; {int(min_b)} - {int(max_b)} bpm",
            }
        )

    def _y_frac(bpm: float) -> float:
        return 1 - (bpm - y_min) / y_range

    return {
        "pills": pills,
        "resting_y_fraction": round(_y_frac(resting_bpm), 3),
        "resting_bpm": round(resting_bpm),
        "target_y_fraction": round(_y_frac(target_bpm), 3)
        if target_bpm is not None
        else None,
        "target_bpm": round(target_bpm) if target_bpm is not None else None,
        "y_min": y_min,
        "y_max": y_max,
        "empty": False,
    }


# ---------------------------------------------------------------------------
#  Viz Builder Strategy (OCP — new metric types = new builder class, no edits)
# ---------------------------------------------------------------------------

@runtime_checkable
class VizBuilder(Protocol):
    """Strategy: build a WidgetViz for a specific source_data_type."""

    def build(
        self,
        ctx: DashboardWidgetService,
        user_id: int,
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
            delta=_delta_str(
                today.count, yesterday.count if yesterday else None, is_integer=True
            ),
        )
        if goal is not None:
            progress = ctx._goal.progress(goal)
            viz.goal_label = f"Target: {int(goal.target_value):,} / day"
            viz.goal_percent = progress.percent
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
        timeline = ctx._activity.heart_rate_timeline(user_id=user_id, date_str=target)

        goal = ctx._resolve_goal(user_id, "heart_rate")
        target_bpm = (
            goal.target_value if goal and goal.direction.value == "decrease" else None
        )
        _chart = _compute_pill_chart(timeline, hr.resting_bpm, color, target_bpm)

        viz = WidgetViz(
            type="pills",
            title="Heart Rate",
            value=f"{hr.resting_bpm:.0f}",
            unit="bpm",
            color=color,
            delta=_delta_str(
                hr.resting_bpm,
                yesterday_hr.resting_bpm if yesterday_hr else None,
                unit=" bpm",
                is_integer=True,
                up_is_good=False,
            ),
            subtitle=f"Min {hr.min_bpm} · Max {hr.max_bpm} · Ø {hr.avg_bpm:.0f}",
        )
        if goal is not None:
            progress = ctx._goal.progress(goal)
            viz.goal_label = f"Target: <{int(goal.target_value)} bpm"
            viz.goal_percent = progress.percent
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
            delta=_delta_str(
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
            delta=_delta_str(
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
            delta=_delta_str(
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
        latest = ctx._measurement_repo.get_latest_by_metric_type(
            metric_type_id=ctx._current_metric_id,
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


_VIZ_BUILDERS: dict[str, VizBuilder] = {
    "steps": StepsVizBuilder(),
    "heart_rate": HeartRateVizBuilder(),
    "sleep": SleepVizBuilder(),
    "nutrition": NutritionVizBuilder(),
    "weight": WeightVizBuilder(),
    "exercise": ExerciseVizBuilder(),
}


# ---------------------------------------------------------------------------
#  Service
# ---------------------------------------------------------------------------

class DashboardWidgetService:
    def __init__(
        self,
        widget_repo: IDashboardWidgetRepository,
        metric_type_repo: IMetricTypeRepository,
        measurement_repo: IMeasurementRepository,
        activity_svc: ActivityAnalysisService,
        sleep_svc: SleepAnalysisService,
        nutrition_svc: NutritionAnalysisService,
        weight_svc: WeightAnalysisService,
        goal_svc: GoalService,
    ) -> None:
        self._widget_repo = widget_repo
        self._metric_type_repo = metric_type_repo
        self._measurement_repo = measurement_repo
        self._activity = activity_svc
        self._sleep = sleep_svc
        self._nutrition = nutrition_svc
        self._weight = weight_svc
        self._goal = goal_svc

        # Request-level caches to optimize N+1 query patterns
        self._goals_cache: list[Goal] | None = None
        self._metrics_cache: dict[int, MetricType] = {}

        # Set per-widget during widget_data() for GenericVizBuilder access
        self._current_metric_id: int | None = None

    def ensure_defaults(self, user_id: int) -> list[DashboardWidget]:
        existing = self._widget_repo.find_by_user(user_id)
        if existing:
            return existing
        enabled_metrics = self._metric_type_repo.find_all(user_id)
        enabled_metrics = [m for m in enabled_metrics if m.widget_enabled]
        widgets: list[DashboardWidget] = []
        for pos, metric in enumerate(enabled_metrics):
            viz_type = _VIZ_TYPE_DEFAULTS.get(metric.source_data_type or "", "number")
            config = json.dumps({"viz_type": viz_type})
            w = DashboardWidget(
                user_id=user_id,
                metric_type_id=metric.id,  # type: ignore[arg-type]
                position=pos,
                size=WidgetSize(metric.widget_size),
                config_json=config,
            )
            self._widget_repo.create(w)
            widgets.append(w)
        return widgets

    def list_widgets(self, user_id: int) -> list[DashboardWidget]:
        return self._widget_repo.find_by_user(user_id)

    def get_widget(self, widget_id: int, user_id: int) -> DashboardWidget:
        w = self._widget_repo.get_by_id(widget_id)
        if w is None or w.user_id != user_id:
            raise ValueError("Widget not found")
        return w

    def add_widget(
        self, user_id: int, metric_type_id: int, size: WidgetSize
    ) -> DashboardWidget:
        existing = self._widget_repo.find_by_user(user_id)
        position = len(existing)
        metric = self._metric_type_repo.get_by_id(metric_type_id)
        viz_type = (
            _VIZ_TYPE_DEFAULTS.get(metric.source_data_type or "", "number")
            if metric
            else "number"
        )
        config = json.dumps({"viz_type": viz_type})
        w = DashboardWidget(
            user_id=user_id,
            metric_type_id=metric_type_id,
            position=position,
            size=size,
            config_json=config,
        )
        return self._widget_repo.create(w)

    def update_widget(
        self, widget_id: int, user_id: int, size: WidgetSize
    ) -> DashboardWidget:
        w = self.get_widget(widget_id, user_id)
        w.size = size
        return self._widget_repo.update(w)

    def delete_widget(self, widget_id: int, user_id: int) -> None:
        w = self.get_widget(widget_id, user_id)
        self._widget_repo.delete(w)

    def reorder(self, user_id: int, ordered_ids: list[int]) -> None:
        self._widget_repo.reorder(user_id, ordered_ids)

    def widget_data(
        self, widget: DashboardWidget, user_id: int, date: str | None = None
    ) -> WidgetViz:
        """Build a WidgetViz for a single widget.

        Always returns a WidgetViz with at least ``title`` and ``type``
        set — even when no data exists (``empty=True``).
        """
        metric = self._metric_type_repo.get_by_id(widget.metric_type_id)
        if metric is None:
            return WidgetViz(
                type="number",
                title=f"Metric #{widget.metric_type_id}",
                empty=True,
                empty_text="Unknown metric",
            )

        sd = metric.source_data_type
        today_str = datetime.today().strftime("%Y-%m-%d")
        target = date if date else today_str

        try:
            config = json.loads(widget.config_json)
        except (json.JSONDecodeError, TypeError):
            config = {}
        viz_type = config.get("viz_type") or _VIZ_TYPE_DEFAULTS.get(sd or "", "number")

        builder = _VIZ_BUILDERS.get(sd or "")
        if builder is None:
            builder = GenericVizBuilder(title=metric.name, unit=metric.unit)
            self._current_metric_id = widget.metric_type_id

        try:
            viz = builder.build(self, user_id=user_id, target=target, color=metric.color or "#64748b")
        except Exception:
            logger.exception("Error building viz for widget %s (sd=%s)", widget.id, sd)
            viz = None

        self._current_metric_id = None

        if viz is None:
            return WidgetViz(
                type=viz_type,
                title=metric.name,
                icon=metric.icon,
                color=metric.color,
                empty=True,
                empty_text=_EMPTY_TEXTS.get(sd or "", "No data recorded yet."),
            )

        # Override viz type with configured type (allows user to change display)
        viz.type = viz_type
        viz.icon = metric.icon
        viz.color = metric.color or viz.color
        return viz

    # ------------------------------------------------------------------
    #  Helpers used by VizBuilder strategies
    # ------------------------------------------------------------------

    def _resolve_goal(self, user_id: int, source_data_type: str) -> Goal | None:
        if self._goals_cache is None:
            self._goals_cache = self._goal.find_all(user_id)
        if not self._metrics_cache:
            for mt in self._metric_type_repo.find_all(user_id):
                if mt.id is not None:
                    self._metrics_cache[mt.id] = mt

        daily_goals: list[Goal] = []
        for g in self._goals_cache:
            if g.frequency.value != "daily":
                continue
            mt = self._metrics_cache.get(g.metric_type_id)
            if mt and mt.source_data_type == source_data_type:
                daily_goals.append(g)
        daily_goals.sort(key=lambda g: g.created_at, reverse=True)
        return daily_goals[0] if daily_goals else None
