from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from salus.services.plugin.context import PluginContext


class BasePlugin:
    def __init__(self, context: "PluginContext") -> None:
        self.context = context

    def initialize(self) -> None:
        """Called when the plugin is registered and initialized."""
        pass

    def on_load(self) -> None:
        """Called when the plugin is activated and loaded."""
        pass

    def on_unload(self) -> None:
        """Called when the plugin is deactivated and unloaded."""
        pass
