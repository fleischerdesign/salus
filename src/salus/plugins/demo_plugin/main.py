import json
from datetime import datetime, timezone
from fastapi import APIRouter

from salus.services.plugin import BasePlugin
from salus.models.measurement import Measurement
from salus.models.goal import Goal


class DemoPlugin(BasePlugin):
    # HookParser
    def can_handle(self, payload: dict | list) -> bool:
        if isinstance(payload, dict):
            return payload.get("source") == "demo"
        return False

    def parse(self, payload: dict | list) -> list[Measurement]:
        if not isinstance(payload, dict):
            return []
        return [
            Measurement(
                data_type="demo_metric",
                source="demo",
                value_numeric=float(payload.get("value", 42.0)),
                value_json=json.dumps(payload),
                start_time=datetime.now(timezone.utc),
                external_id=f"demo-ext-{int(datetime.now(timezone.utc).timestamp())}",
            )
        ]

    # HookWidget
    def get_widget_id(self) -> str:
        return "demo_plugin_widget"

    def get_title(self, locale: str) -> str:
        if locale == "de":
            return "Demo-Plugin-Zusammenfassung"
        return "Demo Plugin Summary"

    def render_html(self, user_id: int, locale: str) -> str:
        try:
            steps = self.context.get_measurements(user_id, data_type="steps", limit=5)
            count = len(steps)
        except Exception as e:
            self.context.log_error(f"Error loading measurements in widget: {e}")
            count = 0

        if locale == "de":
            return f'<div class="demo-card-body"><p>Hallo vom Demo-Plugin! Letzte Schritte-Einträge: <strong>{count}</strong></p></div>'
        return f'<div class="demo-card-body"><p>Hello from Demo Plugin! Recent steps entries: <strong>{count}</strong></p></div>'

    # HookApiRouter
    def register_routes(self, router: APIRouter) -> None:
        @router.get("/hello")
        def hello():
            return {"status": "ok", "message": "Hello from Demo Plugin API"}

    # HookEventSubscriber
    def on_measurement_created(self, measurement: Measurement) -> None:
        self.context.log_info(
            f"DEMO PLUGIN | Captured created measurement of type: {measurement.data_type}"
        )

    def on_goal_achieved(self, goal: Goal) -> None:
        self.context.log_info(
            f"DEMO PLUGIN | Goal achieved! User ID: {goal.user_id}, Metric ID: {goal.metric_type_id}"
        )

    # HookAiCoachContext
    def get_additional_prompt_context(self, user_id: int, date_str: str) -> str:
        return "Note: The user is currently participating in the 'Demo Challenge' and aims to walk extra steps."

    # HookCustomStyle
    def get_custom_css(self) -> str:
        return """
        .demo-card-body {
            background: linear-gradient(135deg, var(--color-indigo-50), var(--color-blue-50));
            padding: 12px;
            border-radius: 8px;
            border: 1px solid var(--color-indigo-100);
            color: var(--color-slate-800);
        }
        [data-theme="dark"] .demo-card-body {
            background: linear-gradient(135deg, var(--color-indigo-950), #0f172a);
            border-color: #1e1b4b;
            color: var(--color-slate-100);
        }
        """

    def get_custom_js(self) -> str:
        return "console.log('Demo Plugin Loaded in browser!');"

    # HookTranslation
    def get_translations(self) -> dict[str, dict[str, str]]:
        return {
            "de": {
                "Demo Summary": "Demo-Zusammenfassung",
            }
        }
