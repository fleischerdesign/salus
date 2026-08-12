import logging
import threading
from collections.abc import Callable

logger = logging.getLogger("salus.services.sharing.tasks")


def run_background(fn: Callable, *args, name: str = "background") -> None:
    """Run fn(*args) on a daemon thread, logging any exception it raises."""

    def _wrapper() -> None:
        try:
            fn(*args)
        except Exception:
            logger.exception("Background task %s failed", name)

    threading.Thread(target=_wrapper, daemon=True, name=name).start()
