from __future__ import annotations

import json
from datetime import datetime, timedelta

from salus.models.analytics import HROHLC, HRTimelinePoint
from salus.models.dashboard import DashboardWidget, WidgetSize
from salus.models.goal import Goal
from salus.repositories.dashboard import DashboardWidgetRepository
from salus.repositories.measurement import MeasurementRepository
from salus.repositories.metric_type import MetricTypeRepository
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.weight import WeightAnalysisService
from salus.services.goal import GoalService

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
    return (datetime.strptime(date_str, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")


def _rounded_segments(stages: list[tuple[str, float, str]]) -> list[dict]:
    total = sum(v for _, v, _ in stages)
    if total <= 0:
        return [{"label": label, "pct": 0, "css_class": css} for label, _, css in stages]
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
        pills.append(
            {
                "min_bpm": int(min_b),
                "max_bpm": int(max_b),
                "color": color,
                "x_fraction": round((idx * 15) / 1440, 4),
            }
        )

    def _y_frac(bpm: float) -> float:
        return 1 - (bpm - y_min) / y_range

    return {
        "pills": pills,
        "resting_y_fraction": round(_y_frac(resting_bpm), 3),
        "resting_bpm": round(resting_bpm),
        "target_y_fraction": round(_y_frac(target_bpm), 3) if target_bpm is not None else None,
        "target_bpm": round(target_bpm) if target_bpm is not None else None,
        "y_min": y_min,
        "y_max": y_max,
        "empty": False,
    }


class DashboardWidgetService:
    def __init__(
        self,
        widget_repo: DashboardWidgetRepository,
        metric_type_repo: MetricTypeRepository,
        measurement_repo: MeasurementRepository,
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

    def add_widget(self, user_id: int, metric_type_id: int, size: WidgetSize) -> DashboardWidget:
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

    def update_widget(self, widget_id: int, user_id: int, size: WidgetSize) -> DashboardWidget:
        w = self.get_widget(widget_id, user_id)
        w.size = size
        return self._widget_repo.update(w)

    def delete_widget(self, widget_id: int, user_id: int) -> None:
        w = self.get_widget(widget_id, user_id)
        self._widget_repo.delete(w)

    def reorder(self, user_id: int, ordered_ids: list[int]) -> None:
        self._widget_repo.reorder(user_id, ordered_ids)

    def widget_data(self, widget: DashboardWidget, user_id: int, date: str | None = None) -> dict:
        metric = self._metric_type_repo.get_by_id(widget.metric_type_id)
        if metric is None:
            return {"widget": widget, "metric": None, "empty": True, "empty_text": "Unknown metric"}

        ctx: dict = {"widget": widget, "metric": metric}
        sd = metric.source_data_type
        today_str = datetime.today().strftime("%Y-%m-%d")
        target = date if date else today_str

        try:
            config = json.loads(widget.config_json)
        except (json.JSONDecodeError, TypeError):
            config = {}
        viz_type = config.get("viz_type") or _VIZ_TYPE_DEFAULTS.get(sd or "", "number")

        viz = self._build_viz(sd, user_id, target, metric.color if metric.color else "#64748b")
        if viz is None:
            ctx["empty"] = True
            ctx["empty_text"] = _EMPTY_TEXTS.get(sd or "", "No data recorded yet.")
            return ctx

        viz["type"] = viz_type
        ctx["viz"] = viz
        ctx["empty"] = False
        return ctx

    # ------------------------------------------------------------------
    #  Viz builders
    # ------------------------------------------------------------------

    def _build_viz(
        self, sd: str | None, user_id: int, target: str, color: str
    ) -> dict | None:
        if sd == "steps":
            return self._build_steps_viz(user_id, target, color)
        if sd == "heart_rate":
            return self._build_heart_rate_viz(user_id, target, color)
        if sd == "sleep":
            return self._build_sleep_viz(user_id, target, color)
        if sd == "nutrition":
            return self._build_nutrition_viz(user_id, target, color)
        if sd == "weight":
            return self._build_weight_viz(user_id, target, color)
        if sd == "exercise":
            return self._build_exercise_viz(user_id, target, color)
        return None

    def _resolve_goal(self, user_id: int, source_data_type: str) -> Goal | None:
        daily_goals: list[Goal] = []
        for g in self._goal.find_all(user_id):
            if g.frequency.value != "daily":
                continue
            mt = self._metric_type_repo.get_by_id(g.metric_type_id)
            if mt and mt.source_data_type == source_data_type:
                daily_goals.append(g)
        daily_goals.sort(key=lambda g: g.created_at, reverse=True)
        return daily_goals[0] if daily_goals else None

    def _build_steps_viz(self, user_id: int, target: str, color: str) -> dict | None:
        trend = self._activity.steps_trend(days=1, user_id=user_id, date=target)
        today = trend[-1] if trend else None
        if not today or today.count <= 0:
            return None

        yesterday_trend = self._activity.steps_trend(
            days=1, user_id=user_id, date=_yesterday(target)
        )
        yesterday = yesterday_trend[-1] if yesterday_trend else None

        goal = self._resolve_goal(user_id, "steps")
        base: dict = {
            "primary_label": "Schritte",
            "primary_value": f"{today.count:,}",
            "primary_unit": "steps",
            "sub": "today",
            "delta": _delta_str(
                today.count, yesterday.count if yesterday else None, is_integer=True
            ),
            "color": color,
        }
        if goal is not None:
            progress = self._goal.progress(goal)
            base["has_goal"] = True
            base["goal"] = int(goal.target_value)
            base["target_label"] = f"Ziel: {int(goal.target_value):,} / Tag"
            base["percent"] = progress.percent
        else:
            base["has_goal"] = False
        return base

    def _build_heart_rate_viz(self, user_id: int, target: str, color: str) -> dict | None:
        hr = self._activity.heart_rate_summary(user_id=user_id, date_str=target)
        if not hr:
            return None

        yesterday_hr = self._activity.heart_rate_summary(
            user_id=user_id, date_str=_yesterday(target)
        )
        timeline = self._activity.heart_rate_timeline(user_id=user_id, date_str=target)

        goal = self._resolve_goal(user_id, "heart_rate")
        target_bpm = goal.target_value if goal and goal.direction.value == "decrease" else None
        chart = _compute_pill_chart(timeline, hr.resting_bpm, color, target_bpm)

        base: dict = {
            "primary_value": f"{hr.resting_bpm:.0f}",
            "primary_unit": "bpm",
            "primary_label": "Puls",
            "delta": _delta_str(
                hr.resting_bpm,
                yesterday_hr.resting_bpm if yesterday_hr else None,
                unit=" bpm",
                is_integer=True,
                up_is_good=False,
            ),
            "stats_line": (
                f"Min {hr.min_bpm} &middot; Max {hr.max_bpm}"
                f" &middot; &Oslash; {hr.avg_bpm:.0f}"
            ),
            "chart": chart,
            "color": color,
        }
        if goal is not None:
            progress = self._goal.progress(goal)
            base["has_goal"] = True
            base["goal"] = int(goal.target_value)
            base["target_label"] = f"Ziel: <{int(goal.target_value)} bpm"
            base["percent"] = progress.percent
            base["goal_direction"] = goal.direction.value
        else:
            base["has_goal"] = False
        return base

    def _build_sleep_viz(self, user_id: int, target: str, color: str) -> dict | None:
        sl = self._sleep.last_night(user_id=user_id, date_str=target)
        if not sl:
            return None

        yesterday_sleep = self._sleep.last_night(
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
        return {
            "primary_label": "Schlaf",
            "primary_value": f"{sl.duration_hours:.1f}",
            "primary_unit": "h",
            "sub": f"{sl.deep_pct:.0f}% Deep &middot; {sl.rem_pct:.0f}% REM",
            "delta": _delta_str(
                sl.duration_hours,
                yesterday_sleep.duration_hours if yesterday_sleep else None,
                unit="h",
            ),
            "segments": segments,
            "color": color,
        }

    def _build_nutrition_viz(self, user_id: int, target: str, color: str) -> dict | None:
        n = self._nutrition.today(user_id=user_id, date_str=target)
        if not n:
            return None

        yesterday_n = self._nutrition.today(
            user_id=user_id, date_str=_yesterday(target)
        )
        total = n.protein_g + n.carbs_g + n.fat_g
        segments = _rounded_segments(
            [
                ("Protein", n.protein_g, "segment-protein"),
                ("Carbs", n.carbs_g, "segment-carbs"),
                ("Fat", n.fat_g, "segment-fat"),
            ]
        ) if total > 0 else []
        return {
            "primary_label": "Ernährung",
            "primary_value": f"{n.total_kcal:.0f}",
            "primary_unit": "kcal",
            "sub": f"P:{n.protein_g:.0f}g C:{n.carbs_g:.0f}g F:{n.fat_g:.0f}g" if total > 0 else "No macros",
            "delta": _delta_str(
                n.total_kcal,
                yesterday_n.total_kcal if yesterday_n else None,
                unit=" kcal",
                is_integer=True,
            ),
            "segments": segments,
            "color": color,
        }

    def _build_weight_viz(self, user_id: int, target: str, color: str) -> dict | None:
        w = self._weight.current(user_id=user_id, date_str=target)
        if not w:
            return None

        yesterday_w = self._weight.current(
            user_id=user_id, date_str=_yesterday(target)
        )
        return {
            "primary_label": "Gewicht",
            "primary_value": f"{w.weight_kg:.1f}",
            "primary_unit": "kg",
            "sub": w.date,
            "delta": _delta_str(
                w.weight_kg,
                yesterday_w.weight_kg if yesterday_w else None,
                unit=" kg",
                up_is_good=False,
            ),
            "color": color,
        }

    def _build_exercise_viz(self, user_id: int, target: str, color: str) -> dict | None:
        sessions = self._activity.exercise_history(days=7, user_id=user_id, limit=5)
        target_sessions = [s for s in sessions if s.date == target]
        if not target_sessions:
            return None

        total_min = sum(s.duration_seconds for s in target_sessions) / 60
        names = set(s.type_name for s in target_sessions)
        return {
            "primary_label": "Training",
            "primary_value": f"{total_min:.0f}",
            "primary_unit": "min",
            "sub": ", ".join(names),
            "color": color,
        }
