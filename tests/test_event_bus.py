import asyncio

import pytest

from salus.services.event_bus import InMemoryEventBus, schedule_publish


@pytest.mark.asyncio
async def test_schedule_publish_notifies_subscriber():
    bus = InMemoryEventBus()
    received = asyncio.Event()

    async def watch():
        async for _ in bus.subscribe("user-1"):
            received.set()
            break

    task = asyncio.create_task(watch())
    await asyncio.sleep(0.01)
    schedule_publish(bus, "user-1")
    await asyncio.wait_for(received.wait(), timeout=1)
    task.cancel()


@pytest.mark.asyncio
async def test_schedule_publish_noop_without_bus():
    schedule_publish(None, "user-1")


@pytest.mark.asyncio
async def test_schedule_publish_noop_without_subscribers():
    bus = InMemoryEventBus()
    schedule_publish(bus, "user-1")


def test_schedule_publish_noop_without_running_loop():
    bus = InMemoryEventBus()
    schedule_publish(bus, "user-1")
