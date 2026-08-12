import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class EventBus(ABC):
    @abstractmethod
    def subscribe(self, user_id: str) -> AsyncGenerator[None, None]:
        ...

    @abstractmethod
    async def publish(self, user_id: str) -> None:
        ...


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[None]]] = {}

    async def subscribe(self, user_id: str) -> AsyncGenerator[None, None]:
        queue: asyncio.Queue[None] = asyncio.Queue(maxsize=32)
        self._subscribers.setdefault(user_id, []).append(queue)
        try:
            while True:
                await queue.get()
                yield
        except asyncio.CancelledError:
            pass
        finally:
            subs = self._subscribers.get(user_id, [])
            if queue in subs:
                subs.remove(queue)

    async def publish(self, user_id: str) -> None:
        for queue in self._subscribers.get(user_id, []):
            try:
                queue.put_nowait(None)
            except asyncio.QueueFull:
                pass


def schedule_publish(event_bus: EventBus | None, user_id: str) -> None:
    """Fire-and-forget an SSE live-sync notification for a user's data change.

    Safe outside a running event loop (CLI, offline contexts): the
    notification is a best-effort hint for other devices to pull, never a
    write dependency. Call after a successful commit on any write channel.
    """
    if event_bus is None:
        return
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    loop.create_task(event_bus.publish(user_id))
