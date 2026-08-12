import json
import logging
from datetime import datetime

from salus.models.dashboard import DashboardWidget, WidgetSize, WidgetViz
from salus.models.goal import Goal
from salus.models.metric_definition import MetricDefinition
from salus.exceptions import NotFoundError
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services._helpers import DEFAULT_METRIC_COLOR
from salus.services.analytics.activity import ActivityAnalysisService
from salus.services.analytics.nutrition import NutritionAnalysisService
from salus.services.analytics.sleep import SleepAnalysisService
from salus.services.analytics.weight import WeightAnalysisService
from salus.services.analytics.blood_pressure import BloodPressureAnalysisService
from salus.services.dashboard_viz.builders import GenericVizBuilder, VIZ_BUILDERS
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
            raise NotFoundError("Widget not found")
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
        metric_color = pref.color if pref else DEFAULT_METRIC_COLOR
        metric_icon = pref.icon if pref else "monitoring"

        sd = metric.source_data_type
        today_str = datetime.today().strftime("%Y-%m-%d")
        target = date if date else today_str

        try:
            config = json.loads(widget.config_json)
        except (json.JSONDecodeError, TypeError):
            config = {}
        viz_type = config.get("viz_type") or VIZ_TYPE_DEFAULTS.get(sd or "", "number")

        builder = VIZ_BUILDERS.get(sd or "")
        if builder is None:
            builder = GenericVizBuilder(
                title=metric.name, unit=metric.unit, metric_code=widget.metric_code
            )

        try:
            viz = builder.build(self, user_id=user_id, target=target, color=metric_color)
        except Exception:
            logger.exception("Error building viz for widget %s (sd=%s)", widget.id, sd)
            viz = None

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
