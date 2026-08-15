from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

from salus.models.habit import HabitLog
from salus.schemas.commands import ToggleHabitCheckPayload
from salus.services._helpers import uid
from salus.services.command_registry import CommandResult, register
from salus.services.habit import habit_streak_stats
from salus.services.serialization import serialize_record
from salus.services.timezone import user_today

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User

_LOG_FIELDS = (
    "id", "habit_id", "user_id", "log_date", "completed",
    "completed_at", "notes", "created_at", "deleted_at",
)


@register("toggle_habit_check")
class ToggleHabitCheckHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = ToggleHabitCheckPayload.model_validate(payload)
        user_id = uid(user)
        habit = uow.habits.get_by_id(data.habit_id)
        if not habit or habit.user_id != user_id:
            return CommandResult(status="not_found", message="Habit not found")

        today = user_today(uow.session, user_id)
        now = datetime.now(timezone.utc)
        existing = uow.habit_logs.find_by_habit_and_date(data.habit_id, today)
        if existing:
            existing.completed = not existing.completed
            existing.completed_at = now if existing.completed else None
            uow.habit_logs.add(existing)
            log = existing
            status = "updated"
        else:
            log = HabitLog(
                habit_id=data.habit_id,
                user_id=user_id,
                log_date=today,
                completed=True,
                completed_at=now,
            )
            uow.habit_logs.add(log)
            status = "created"

        uow.commit()
        uow.session.refresh(log)

        stats = habit_streak_stats(uow, data.habit_id, user_id, today)
        return CommandResult(
            status=status,
            id=log.id,
            record=serialize_record(log, list(_LOG_FIELDS)),
            extra={
                "completed": log.completed,
                "current_streak": stats["current_streak"],
                "longest_streak": stats["longest_streak"],
                "completion_rate": stats["completion_rate"],
            },
        )
