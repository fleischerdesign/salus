"""Minimal asyncio scheduler for periodic background jobs.

A dependency-free alternative to APScheduler: a single asyncio task ticks and
runs due jobs via ``asyncio.to_thread`` (SQLAlchemy's synchronous Session must
not block the event loop). Each job opens its own session through a
``session_factory``. Jobs first become due after their ``interval_seconds``
elapses, so short-lived processes (tests) never run them.

See ADR-007 for the motivating use case (data-quality recheck) and the intent
that future periodic work reuses this scheduler.
"""
from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable
from typing import Any, Protocol

logger = logging.getLogger("salus.scheduler")

SessionFactory = Callable[[], Any]


class ScheduledJob(Protocol):
    name: str
    interval_seconds: int

    def run(self, session_factory: SessionFactory) -> None: ...


class AppScheduler:
    def __init__(self, session_factory: SessionFactory, tick_seconds: float = 1.0) -> None:
        self._session_factory = session_factory
        self._tick_seconds = tick_seconds
        self._jobs: list[ScheduledJob] = []
        self._next_run: dict[str, float] = {}
        self._task: asyncio.Task[None] | None = None

    def add(self, job: ScheduledJob) -> None:
        self._jobs.append(job)
        self._next_run[job.name] = time.monotonic() + job.interval_seconds

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    async def _loop(self) -> None:
        while True:
            now = time.monotonic()
            for job in self._jobs:
                if now >= self._next_run.get(job.name, now + job.interval_seconds):
                    self._next_run[job.name] = now + job.interval_seconds
                    try:
                        await asyncio.to_thread(job.run, self._session_factory)
                    except Exception:
                        logger.exception("Scheduler job '%s' failed", job.name)
            await asyncio.sleep(self._tick_seconds)
