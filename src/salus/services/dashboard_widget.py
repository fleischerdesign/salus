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

    def widget_data(self, widget: DashboardWidget) -> dict:
        metric = self._metric_type_repo.get_by_id(widget.metric_type_id)
        if metric is None:
            return {"widget": widget, "metric": None, "empty": True, "empty_text": "Unknown metric"}

        ctx: dict = {"widget": widget, "metric": metric}
        sd = metric.source_data_type

        if sd == "steps":
            trend = self._activity.steps_trend(days=7)
            today = trend[-1] if trend else None
            if today and today.count > 0:
                ctx["value"] = f"{today.count:,}"
                ctx["sub"] = "today"
                ctx["goal"] = 10000
                ctx["percent"] = min(int(today.count / 10000 * 100), 100)
                ctx["sparkline"] = _compute_sparkline([float(d.count) for d in trend])
            else:
                ctx["value"] = "—"

        elif sd == "heart_rate":
            hr = self._activity.heart_rate_summary()
            if hr:
                ctx["value"] = f"{hr.resting_bpm:.0f}"
                ctx["unit"] = "bpm"
                ctx["sub"] = f"Avg {hr.avg_bpm:.0f} &middot; {hr.min_bpm}–{hr.max_bpm}"
            else:
                ctx["value"] = "—"

        elif sd == "sleep":
            sl = self._sleep.last_night()
            if sl:
                ctx["value"] = f"{sl.duration_hours:.1f}h"
                ctx["sub"] = f"{sl.deep_pct:.0f}% Deep &middot; {sl.rem_pct:.0f}% REM"
            else:
                ctx["value"] = "—"

        elif sd == "nutrition":
            n = self._nutrition.today()
            if n:
                ctx["value"] = f"{n.total_kcal:.0f}"
                ctx["unit"] = "kcal"
                total = n.protein_g + n.carbs_g + n.fat_g
                if total > 0:
                    ctx["protein_pct"] = n.protein_g / total * 100
                    ctx["carbs_pct"] = n.carbs_g / total * 100
                    ctx["fat_pct"] = n.fat_g / total * 100
                    ctx["sub"] = f"P:{n.protein_g:.0f}g C:{n.carbs_g:.0f}g F:{n.fat_g:.0f}g"
                else:
                    ctx["sub"] = "No macros"
            else:
                ctx["value"] = "—"

        elif sd == "weight":
            w = self._weight.current()
            if w:
                ctx["value"] = f"{w.weight_kg:.1f}"
                ctx["unit"] = "kg"
                ctx["sub"] = "latest"
            else:
                ctx["value"] = "—"

        else:
            ctx["value"] = "—"

        ctx["empty"] = ctx.get("value", "—") == "—"
        if ctx["empty"]:
            ctx["empty_text"] = _EMPTY_TEXTS.get(sd or "", "No data recorded yet.")
        return ctx
