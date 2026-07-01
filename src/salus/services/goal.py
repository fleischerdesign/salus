from datetime import date, datetime, timedelta, timezone

from salus.exceptions import NotFoundError
from salus.models.analytics import GoalProgress
from salus.models.goal import Goal, GoalDirection, GoalFrequency
from salus.models.measurement import Measurement
from salus.repositories.protocols import IGoalRepository, IMeasurementRepository
from salus.schemas.goal import GoalCreate
from salus.services.analytics.calculations import compute_goal_progress


class GoalService:
    def __init__(self, repo: IGoalRepository, measurement_repo: IMeasurementRepository) -> None:
        self._repo = repo
        self._measurement_repo = measurement_repo

    def get(self, goal_id: int, user_id: int) -> Goal:
        goal = self._repo.get_by_id(goal_id)
        if goal is None:
            raise NotFoundError(f"Goal {goal_id} not found")
        if goal.user_id != user_id:
            raise NotFoundError(f"Goal {goal_id} not found")
        return goal

    def find_all(self, user_id: int) -> list[Goal]:
        return self._repo.find_by_user(user_id)

    def create(self, data: GoalCreate, user_id: int) -> Goal:
        goal = Goal(
            user_id=user_id,
            metric_type_id=data.metric_type_id,
            target_value=data.target_value,
            direction=data.direction,
            frequency=data.frequency,
            deadline=data.deadline,
        )
        return self._repo.create(goal)

    def delete(self, goal_id: int, user_id: int) -> None:
        goal = self.get(goal_id, user_id)
        self._repo.delete(goal)

    def progress(self, goal: Goal) -> GoalProgress:
        entries = self._measurement_repo.find_by_metric_type(
            goal.metric_type_id, goal.user_id
        )
        if goal.frequency == GoalFrequency.DAILY:
            entries = _filter_today(entries)
        elif goal.frequency == GoalFrequency.WEEKLY:
            entries = _filter_this_week(entries)

        current = _extract_current_value(entries, goal.direction)
        deadline_passed = goal.deadline is not None and goal.deadline < date.today()

        percent, status, fulfilled = compute_goal_progress(
            current_value=current,
            target_value=goal.target_value,
            direction=goal.direction,
            frequency=goal.frequency,
            deadline_passed=deadline_passed,
        )

        return GoalProgress(
            goal_id=goal.id or 0,
            current_value=current,
            target_value=goal.target_value,
            percent=percent,
            status=status,
            is_fulfilled=fulfilled,
        )


def _filter_today(entries: list[Measurement]) -> list[Measurement]:
    today = datetime.now(timezone.utc).date()
    return [e for e in entries if e.start_time.date() == today]


def _filter_this_week(entries: list[Measurement]) -> list[Measurement]:
    today = datetime.now(timezone.utc).date()
    monday = today - timedelta(days=today.weekday())
    return [e for e in entries if e.start_time.date() >= monday]


def _extract_current_value(
    entries: list[Measurement], direction: GoalDirection
) -> float | None:
    if not entries:
        return None
    try:
        values = [float(e.value_text) for e in entries if e.value_text]
        values += [float(e.value_numeric) for e in entries
                   if e.value_numeric is not None and e.value_text is None]
    except (ValueError, TypeError):
        return None
    if not values:
        return None
    if direction == GoalDirection.INCREASE:
        return max(values)
    return min(values)
