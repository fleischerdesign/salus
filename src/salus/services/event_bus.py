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
