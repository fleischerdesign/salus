from __future__ import annotations

from typing import Any, TYPE_CHECKING

from salus.models.goal import Goal
from salus.services.command_registry import CommandResult, register

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User


@register("create_goal")
class CreateGoalHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        goal = Goal(
            id=payload.get("id"),
            user_id=user.id,  # pyright: ignore[reportArgumentType]
            metric_type_id=payload["metric_type_id"],
            target_value=payload["target_value"],
            direction=payload.get("direction", "increase"),
            frequency=payload.get("frequency", "daily"),
            deadline=payload.get("deadline"),
        )
        uow.goals.add(goal)
        uow.commit()
        uow.session.refresh(goal)
        record: dict[str, Any] = {k: getattr(goal, k, None) for k in
            ("id", "user_id", "metric_type_id", "target_value", "direction",
             "frequency", "deadline", "is_active", "created_at", "updated_at", "deleted_at")}
        return CommandResult(status="created", record=record, id=goal.id)


@register("delete_goal")
class DeleteGoalHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        goal_id = payload.get("id")
        if not goal_id:
            return CommandResult(status="error", message="id is required")
        goal = uow.goals.get_by_id(goal_id)  # pyright: ignore[reportArgumentType]
        if not goal:
            return CommandResult(status="not_found", id=goal_id)
        if goal.user_id != user.id:  # pyright: ignore[reportAttributeAccessIssue]
            return CommandResult(status="forbidden", id=goal_id)
        uow.goals.delete(goal)
        uow.commit()
        return CommandResult(status="deleted", id=goal_id)