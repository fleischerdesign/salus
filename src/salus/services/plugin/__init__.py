from salus.services.plugin.base import BasePlugin
from salus.services.plugin.context import PluginContext
from salus.services.plugin.hooks import (
    HookRegistry,
    HookParser,
    HookApiRouter,
    HookEventSubscriber,
    HookAiCoachContext,
    HookBackgroundTask,
    HookExporter,
    HookAuthProvider,
    HookIngestionInterceptor,
    HookTranslation,
    HookSchemaExtension,
    HookApplicationLifecycle,
    HookGoalValidator,
    HookMetricSynthesizer,
)
from salus.services.plugin.manager import PluginManager

__all__ = [
    "BasePlugin",
    "PluginContext",
    "HookRegistry",
    "HookParser",
    "HookApiRouter",
    "HookEventSubscriber",
    "HookAiCoachContext",
    "HookBackgroundTask",
    "HookExporter",
    "HookAuthProvider",
    "HookIngestionInterceptor",
    "HookTranslation",
    "HookSchemaExtension",
    "HookApplicationLifecycle",
    "HookGoalValidator",
    "HookMetricSynthesizer",
    "PluginManager",
]
