from datetime import datetime, timedelta

from salus.models.dashboard import DashboardWidget, WidgetSize
from salus.repositories.dashboard import DashboardWidgetRepository
from salus.repositories.measurement import MeasurementRepository
from salus.repositories.metric_type import MetricTypeRepository
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.weight import WeightAnalysisService


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


def _delta_str(current: float | None, previous: float | None, unit: str = "", is_integer: bool = False, up_is_good: bool = True) -> str | None:
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
        return f'<span class="widget-delta widget-delta--{css_class}">{direction} {diff_str}{unit}</span>'
    if diff > 0 and pct >= 1:
        return f'<span class="widget-delta widget-delta--{css_class}">{direction} {pct:.0f}%</span>'
    return f'<span class="widget-delta widget-delta--{css_class}">{direction} {diff_str}</span>'


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
    ) -> None:
        self._widget_repo = widget_repo
        self._metric_type_repo = metric_type_repo
        self._measurement_repo = measurement_repo
        self._activity = activity_svc
        self._sleep = sleep_svc
        self._nutrition = nutrition_svc
        self._weight = weight_svc

    def ensure_defaults(self, user_id: int) -> list[DashboardWidget]:
        existing = self._widget_repo.find_by_user(user_id)
        if existing:
            return existing
        enabled_metrics = self._metric_type_repo.find_all(user_id)
        enabled_metrics = [m for m in enabled_metrics if m.widget_enabled]
        widgets: list[DashboardWidget] = []
        for pos, metric in enumerate(enabled_metrics):
            w = DashboardWidget(
                user_id=user_id,
                metric_type_id=metric.id,  # type: ignore[arg-type]
                position=pos,
                size=WidgetSize(metric.widget_size),
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
        w = DashboardWidget(
            user_id=user_id,
            metric_type_id=metric_type_id,
            position=position,
            size=size,
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

        if sd == "steps":
            trend = self._activity.steps_trend(days=7, user_id=user_id, date=target)
            today = trend[-1] if trend else None
            if today and today.count > 0:
                ctx["value"] = f"{today.count:,}"
                ctx["unit"] = "steps"
                ctx["sub"] = "today"

                yesterday_date = (datetime.strptime(target, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                yesterday_trend = self._activity.steps_trend(days=1, user_id=user_id, date=yesterday_date)
                yesterday = yesterday_trend[-1] if yesterday_trend else None
                ctx["delta"] = _delta_str(
                    today.count, yesterday.count if yesterday else None, is_integer=True
                )
            else:
                ctx["value"] = "—"

        elif sd == "heart_rate":
            hr = self._activity.heart_rate_summary(user_id=user_id, date_str=target)
            if hr:
                ctx["value"] = f"{hr.avg_bpm:.0f}"
                ctx["unit"] = "bpm"
                ctx["sub"] = f"Resting {hr.resting_bpm:.0f} &middot; {hr.min_bpm}–{hr.max_bpm}"

                yesterday_date = (datetime.strptime(target, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                yesterday_hr = self._activity.heart_rate_summary(user_id=user_id, date_str=yesterday_date)
                ctx["delta"] = _delta_str(
                    hr.avg_bpm, yesterday_hr.avg_bpm if yesterday_hr else None,
                    unit=" bpm", is_integer=True, up_is_good=False,
                )
            else:
                ctx["value"] = "—"

        elif sd == "sleep":
            sl = self._sleep.last_night(user_id=user_id, date_str=target)
            if sl:
                ctx["value"] = f"{sl.duration_hours:.1f}h"
                ctx["sub"] = f"{sl.deep_pct:.0f}% Deep &middot; {sl.rem_pct:.0f}% REM"

                yesterday_date = (datetime.strptime(target, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                yesterday_sleep = self._sleep.last_night(user_id=user_id, date_str=yesterday_date)
                ctx["delta"] = _delta_str(
                    sl.duration_hours, yesterday_sleep.duration_hours if yesterday_sleep else None,
                    unit="h",
                )
            else:
                ctx["value"] = "—"

        elif sd == "nutrition":
            n = self._nutrition.today(user_id=user_id, date_str=target)
            if n:
                ctx["value"] = f"{n.total_kcal:.0f}"
                ctx["unit"] = "kcal"
                total = n.protein_g + n.carbs_g + n.fat_g
                if total > 0:
                    ctx["protein_pct"] = n.protein_g / total * 100
                    ctx["carbs_pct"] = n.carbs_g / total * 100
                    ctx["fat_pct"] = n.fat_g / total * 100
                    ctx["sub"] = f"{n.protein_g:.0f}g Protein &middot; {n.carbs_g:.0f}g Carbs &middot; {n.fat_g:.0f}g Fat"

                    yesterday_date = (datetime.strptime(target, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                    yesterday_n = self._nutrition.today(user_id=user_id, date_str=yesterday_date)
                    ctx["delta"] = _delta_str(
                        n.total_kcal, yesterday_n.total_kcal if yesterday_n else None,
                        unit=" kcal", is_integer=True,
                    )
                else:
                    ctx["sub"] = "No macros"
            else:
                ctx["value"] = "—"

        elif sd == "weight":
            w = self._weight.current(user_id=user_id, date_str=target)
            if w:
                ctx["value"] = f"{w.weight_kg:.1f}"
                ctx["unit"] = "kg"

                yesterday_date = (datetime.strptime(target, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                yesterday_w = self._weight.current(user_id=user_id, date_str=yesterday_date)
                ctx["delta"] = _delta_str(
                    w.weight_kg, yesterday_w.weight_kg if yesterday_w else None,
                    unit=" kg", up_is_good=False,
                )
            else:
                ctx["value"] = "—"

        elif sd == "exercise":
            sessions = self._activity.exercise_history(days=7, user_id=user_id, limit=10)
            target_sessions = [
                s for s in sessions
                if s.date == target
            ]
            if target_sessions:
                total_min = sum(s.duration_seconds for s in target_sessions) / 60
                total_cal = sum(s.calories for s in target_sessions)
                total_dist = sum(s.distance_meters for s in target_sessions)
                ctx["value"] = f"{total_min:.0f}"
                ctx["unit"] = "min"

                parts = []
                if total_cal > 0:
                    parts.append(f"{total_cal:.0f} kcal")
                if total_dist > 0:
                    km = total_dist / 1000
                    parts.append(f"{km:.1f} km")
                if parts:
                    ctx["sub"] = " &middot; ".join(parts)

                yesterday_date = (datetime.strptime(target, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                yesterday_sessions = [s for s in sessions if s.date == yesterday_date]
                yesterday_min = sum(s.duration_seconds for s in yesterday_sessions) / 60 if yesterday_sessions else None
                ctx["delta"] = _delta_str(
                    total_min, yesterday_min,
                    unit=" min", is_integer=True,
                )
            else:
                ctx["value"] = "—"

        else:
            ctx["value"] = "—"

        ctx["empty"] = ctx.get("value", "—") == "—"
        if ctx["empty"]:
            ctx["empty_text"] = _EMPTY_TEXTS.get(sd or "", "No data recorded yet.")
        return ctx
