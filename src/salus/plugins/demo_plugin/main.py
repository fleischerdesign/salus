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
    def get_additional_prompt_context(self, user_id: str, date_str: str) -> str:
        return "Note: The user is currently participating in the 'Demo Challenge' and aims to walk extra steps."

    # HookTranslation
    def get_translations(self) -> dict[str, dict[str, str]]:
        return {
            "de": {
                "Demo Summary": "Demo-Zusammenfassung",
            }
        }
