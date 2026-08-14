import asyncio

from salus.services.scheduler import AppScheduler


class _FakeJob:
    name = "fake_job"
    interval_seconds = 1

    def __init__(self) -> None:
        self.runs = 0

    def run(self, session_factory) -> None:
        self.runs += 1


def test_scheduler_runs_due_job():
    job = _FakeJob()
    job.interval_seconds = 0.05
    scheduler = AppScheduler(lambda: None, tick_seconds=0.02)

    async def scenario() -> None:
        scheduler.add(job)
        await scheduler.start()
        await asyncio.sleep(0.2)
        await scheduler.stop()

    asyncio.run(scenario())
    assert job.runs >= 1


def test_scheduler_does_not_run_immediately():
    job = _FakeJob()  # interval 1s
    scheduler = AppScheduler(lambda: None, tick_seconds=0.01)

    async def scenario() -> None:
        scheduler.add(job)
        await scheduler.start()
        await asyncio.sleep(0.05)
        await scheduler.stop()

    asyncio.run(scenario())
    assert job.runs == 0
