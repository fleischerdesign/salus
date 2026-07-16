import logging
from datetime import date, datetime, timedelta, timezone

from salus.exceptions import NotFoundError
from salus.models.analytics import GoalProgress
from salus.models.goal import Goal, GoalDirection, GoalFrequency
from salus.models.measurement import Measurement
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.goal import GoalCreate
from salus.services.analytics.calculations import compute_goal_progress
from salus.services.analytics.stats import (
    linear_regression,
    prediction_interval,
)
from salus.services.plugin.hooks import HookRegistry

logger = logging.getLogger("salus.services.goal")


class GoalService:
    def __init__(
        self,
        uow: IUnitOfWork,
        registry: HookRegistry | None = None,
    ) -> None:
        self.uow = uow
        self._registry = registry

    def get(self, goal_id: str, user_id: str) -> Goal:
        goal = self.uow.goals.get_by_id(goal_id)
        if goal is None:
            raise NotFoundError(f"Goal {goal_id} not found")
        if goal.user_id != user_id:
            raise NotFoundError(f"Goal {goal_id} not found")
        return goal

    def find_all(self, user_id: str) -> list[Goal]:
        return self.uow.goals.find_by_user(user_id)

    def create(self, data: GoalCreate, user_id: str) -> Goal:
        goal = Goal(
            user_id=user_id,
            metric_code=data.metric_code,
            target_value=data.target_value,
            direction=data.direction,
            frequency=data.frequency,
            deadline=data.deadline,
        )
        return self.uow.goals.create(goal)

    def delete(self, goal_id: str, user_id: str) -> None:
        goal = self.get(goal_id, user_id)
        self.uow.goals.delete(goal)

    def compute_progress(self, goal: Goal) -> GoalProgress:
        entries = self.uow.measurements.find_by_metric_type(
            goal.metric_code, goal.user_id
        )

        plugin_fulfilled = None
        if self._registry:
            goal_type = str(goal.frequency.value)
            for validator in self._registry.goal_validators:
                try:
                    if validator.can_evaluate(goal_type):
                        plugin_fulfilled = validator.evaluate(goal, entries)
                        break
                except Exception as e:
                    logger.error(f"Error executing plugin goal validator: {e}")

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

        if plugin_fulfilled is not None:
            fulfilled = plugin_fulfilled
            status = "fulfilled" if fulfilled else "pending"
            percent = 100 if fulfilled else 0

        forecast: dict = {}
        if (
            goal.frequency == GoalFrequency.ONCE
            and goal.deadline is not None
            and not deadline_passed
        ):
            forecast = self._compute_deadline_forecast(goal, entries)

        if fulfilled and self._registry:
            for sub in self._registry.event_subscribers:
                try:
                    sub.on_goal_achieved(goal)
                except Exception as e:
                    logger.error(
                        f"Error notifying event subscriber on goal achieved: {e}"
                    )

        return GoalProgress(
            goal_id=goal.id or "",
            current_value=current,
            target_value=goal.target_value,
            percent=int(percent),
            status=status,
            is_fulfilled=fulfilled,
            on_track=forecast.get("on_track"),
            predicted_value=forecast.get("predicted"),
            predicted_ci_lower=forecast.get("ci_lower"),
            predicted_ci_upper=forecast.get("ci_upper"),
            trend_r_squared=forecast.get("r_squared"),
        )

    def _compute_deadline_forecast(
        self, goal: Goal, entries: list[Measurement]
    ) -> dict:
        entries_sorted = sorted(entries, key=lambda e: e.start_time)
        if len(entries_sorted) < 3:
            return {}
        xs: list[float] = []
        ys: list[float] = []
        for e in entries_sorted:
            days_since = (e.start_time.date() - goal.created_at.date()).days
            xs.append(float(days_since))
            if e.value_numeric is not None:
                ys.append(e.value_numeric)
            elif e.value_text:
                try:
                    ys.append(float(e.value_text))
                except (ValueError, TypeError):
                    continue
        if len(ys) < 3:
            return {}
        xs_slice = xs[-len(ys):]
        reg = linear_regression(xs_slice, ys)
        if reg is None:
            return {}
        if goal.deadline is None:
            return {}
        days_total = (goal.deadline - goal.created_at.date()).days
        pi = prediction_interval(reg, float(days_total), confidence=0.80)
        if pi is None:
            return {}
        if goal.direction == GoalDirection.INCREASE:
            on_track = pi.lower >= goal.target_value
        else:
            on_track = pi.upper <= goal.target_value
        return {
            "on_track": on_track,
            "predicted": round(pi.point_estimate, 2),
            "ci_lower": round(pi.lower, 2),
            "ci_upper": round(pi.upper, 2),
            "r_squared": round(reg.r_squared, 4),
        }


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
        values += [
            float(e.value_numeric)
            for e in entries
            if e.value_numeric is not None and e.value_text is None
        ]
    except (ValueError, TypeError):
        return None
    if not values:
        return None
    if direction == GoalDirection.INCREASE:
        return max(values)
    return min(values)
