from typing import Any, Protocol, runtime_checkable
from fastapi import APIRouter
from sqlmodel import SQLModel

from salus.models.measurement import Measurement
from salus.models.goal import Goal
from salus.models.user import User


@runtime_checkable
class HookParser(Protocol):
    def can_handle(self, payload: dict | list) -> bool:
        ...

    def parse(self, payload: dict | list) -> list[Measurement]:
        ...


@runtime_checkable
class HookWidget(Protocol):
    def get_widget_id(self) -> str:
        ...

    def get_title(self, locale: str) -> str:
        ...

    def render_html(self, user_id: int, locale: str) -> str:
        ...


@runtime_checkable
class HookApiRouter(Protocol):
    def register_routes(self, router: APIRouter) -> None:
        ...


@runtime_checkable
class HookEventSubscriber(Protocol):
    def on_measurement_created(self, measurement: Measurement) -> None:
        ...

    def on_goal_achieved(self, goal: Goal) -> None:
        ...


@runtime_checkable
class HookAiCoachContext(Protocol):
    def get_additional_prompt_context(self, user_id: int, date_str: str) -> str:
        ...


@runtime_checkable
class HookBackgroundTask(Protocol):
    def get_interval_seconds(self) -> int:
        ...

    def run_task(self) -> None:
        ...


@runtime_checkable
class HookExporter(Protocol):
    def get_format_name(self) -> str:
        ...

    def export_data(self, measurements: list[Measurement]) -> bytes:
        ...


@runtime_checkable
class HookAuthProvider(Protocol):
    def get_provider_name(self) -> str:
        ...

    def authenticate(self, credentials: dict) -> User | None:
        ...


@runtime_checkable
class HookIngestionInterceptor(Protocol):
    def intercept(self, measurements: list[Measurement]) -> list[Measurement]:
        ...


@runtime_checkable
class HookNavigation(Protocol):
    def get_navigation_items(self) -> list[dict[str, Any]]:
        ...


@runtime_checkable
class HookTranslation(Protocol):
    def get_translations(self) -> dict[str, dict[str, str]]:
        ...


@runtime_checkable
class HookSchemaExtension(Protocol):
    def get_models(self) -> list[type[SQLModel]]:
        ...


@runtime_checkable
class HookApplicationLifecycle(Protocol):
    def on_startup(self) -> None:
        ...

    def on_shutdown(self) -> None:
        ...


@runtime_checkable
class HookGoalValidator(Protocol):
    def can_evaluate(self, goal_type: str) -> bool:
        ...

    def evaluate(self, goal: Goal, measurements: list[Measurement]) -> bool:
        ...


@runtime_checkable
class HookMetricSynthesizer(Protocol):
    def get_synthetic_metric_name(self) -> str:
        ...

    def synthesize(self, user_id: int, measurements: list[Measurement]) -> list[Measurement]:
        ...


@runtime_checkable
class HookCustomStyle(Protocol):
    def get_custom_css(self) -> str:
        ...

    def get_custom_js(self) -> str:
        ...


class HookRegistry:
    def __init__(self) -> None:
        self.parsers: list[HookParser] = []
        self.widgets: list[HookWidget] = []
        self.api_routers: list[HookApiRouter] = []
        self.event_subscribers: list[HookEventSubscriber] = []
        self.ai_coach_contexts: list[HookAiCoachContext] = []
        self.background_tasks: list[HookBackgroundTask] = []
        self.exporters: list[HookExporter] = []
        self.auth_providers: list[HookAuthProvider] = []
        self.ingestion_interceptors: list[HookIngestionInterceptor] = []
        self.navigations: list[HookNavigation] = []
        self.translations: list[HookTranslation] = []
        self.schemas: list[HookSchemaExtension] = []
        self.lifecycles: list[HookApplicationLifecycle] = []
        self.goal_validators: list[HookGoalValidator] = []
        self.metric_synthesizers: list[HookMetricSynthesizer] = []
        self.custom_styles: list[HookCustomStyle] = []

    def register(self, plugin: Any) -> None:
        """Inspects plugin for hook implementations and registers them."""
        if isinstance(plugin, HookParser):
            self.parsers.append(plugin)
        if isinstance(plugin, HookWidget):
            self.widgets.append(plugin)
        if isinstance(plugin, HookApiRouter):
            self.api_routers.append(plugin)
        if isinstance(plugin, HookEventSubscriber):
            self.event_subscribers.append(plugin)
        if isinstance(plugin, HookAiCoachContext):
            self.ai_coach_contexts.append(plugin)
        if isinstance(plugin, HookBackgroundTask):
            self.background_tasks.append(plugin)
        if isinstance(plugin, HookExporter):
            self.exporters.append(plugin)
        if isinstance(plugin, HookAuthProvider):
            self.auth_providers.append(plugin)
        if isinstance(plugin, HookIngestionInterceptor):
            self.ingestion_interceptors.append(plugin)
        if isinstance(plugin, HookNavigation):
            self.navigations.append(plugin)
        if isinstance(plugin, HookTranslation):
            self.translations.append(plugin)
        if isinstance(plugin, HookSchemaExtension):
            self.schemas.append(plugin)
        if isinstance(plugin, HookApplicationLifecycle):
            self.lifecycles.append(plugin)
        if isinstance(plugin, HookGoalValidator):
            self.goal_validators.append(plugin)
        if isinstance(plugin, HookMetricSynthesizer):
            self.metric_synthesizers.append(plugin)
        if isinstance(plugin, HookCustomStyle):
            self.custom_styles.append(plugin)

    def unregister(self, plugin: Any) -> None:
        """Removes all hook registrations for this plugin instance."""
        for attr in self.__dict__.values():
            if isinstance(attr, list):
                if plugin in attr:
                    attr.remove(plugin)
