from collections import defaultdict
from datetime import date, datetime, timezone

from salus.exceptions import NotFoundError
from salus.models.habit import Habit, HabitLog
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.habit import HabitCreate, HabitUpdate


def _compute_streak_dates(dates: list[date], today: date) -> tuple[int, int]:
    if not dates:
        return 0, 0
    unique = sorted(set(dates), reverse=True)
    current = 0
    expected = today
    for d in unique:
        if d == expected:
            current += 1
            expected = _prev_day(expected)
        elif d < expected:
            break
    longest = 1
    run = 1
    for i in range(1, len(unique)):
        if _prev_day(unique[i - 1]) == unique[i]:
            run += 1
        else:
            run = 1
        if run > longest:
            longest = run
    return current, longest


def _prev_day(d: date) -> date:
    from datetime import timedelta
    return d - timedelta(days=1)


class HabitService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def find_all(self, user_id: str) -> list[Habit]:
        return self.uow.habits.find_by_user(user_id)

    def get(self, habit_id: str, user_id: str) -> Habit:
        h = self.uow.habits.get_by_id(habit_id)
        if h is None or h.user_id != user_id:
            raise NotFoundError(f"Habit {habit_id} not found")
        return h

    def create(self, data: HabitCreate, user_id: str) -> Habit:
        h = Habit(
            user_id=user_id,
            name=data.name,
            description=data.description,
            color=data.color,
            icon=data.icon,
            frequency=data.frequency,
            target_count=data.target_count,
            days_bitmask=data.days_bitmask,
            stack_hint=data.stack_hint,
        )
        return self.uow.habits.create(h)

    def update(self, habit_id: str, user_id: str, data: HabitUpdate) -> Habit:
        h = self.get(habit_id, user_id)
        if data.name is not None:
            h.name = data.name
        if data.description is not None:
            h.description = data.description
        if data.color is not None:
            h.color = data.color
        if data.icon is not None:
            h.icon = data.icon
        if data.frequency is not None:
            h.frequency = data.frequency
        if data.target_count is not None:
            h.target_count = data.target_count
        if data.days_bitmask is not None:
            h.days_bitmask = data.days_bitmask
        if data.stack_hint is not None:
            h.stack_hint = data.stack_hint
        if data.is_archived is not None:
            h.is_archived = data.is_archived
        return self.uow.habits.update(h)

    def delete(self, habit_id: str, user_id: str) -> None:
        h = self.get(habit_id, user_id)
        self.uow.habits.delete(h)

    def toggle_check(self, habit_id: str, user_id: str) -> dict:
        self.get(habit_id, user_id)
        today = date.today()
        existing = self.uow.habit_logs.find_by_habit_and_date(habit_id, today)
        if existing:
            existing.completed = not existing.completed
            existing.completed_at = datetime.now(timezone.utc) if existing.completed else None
            self.uow.habit_logs.update(existing)
            log = existing
        else:
            log = HabitLog(
                habit_id=habit_id,
                user_id=user_id,
                log_date=today,
                completed=True,
                completed_at=datetime.now(timezone.utc),
            )
            self.uow.habit_logs.create(log)

        all_logs = self.uow.habit_logs.find_by_habit_and_user(habit_id, user_id)
        completed_dates = [log.log_date for log in all_logs if log.completed]
        current_streak, longest_streak = _compute_streak_dates(completed_dates, today)

        total_days = (today - min(completed_dates or [today])).days + 1
        rate = len(completed_dates) / max(total_days, 1)

        return {
            "completed": log.completed,
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "completion_rate": round(rate, 3),
        }

    def get_logs(self, habit_id: str, user_id: str) -> list[HabitLog]:
        self.get(habit_id, user_id)
        return self.uow.habit_logs.find_by_habit_and_user(habit_id, user_id)

    def get_stats(self, habit_id: str, user_id: str) -> dict:
        self.get(habit_id, user_id)
        all_logs = self.uow.habit_logs.find_by_habit_and_user(habit_id, user_id)
        completed_dates = [log.log_date for log in all_logs if log.completed]
        today = date.today()
        current_streak, longest_streak = _compute_streak_dates(completed_dates, today)
        total_days = (today - min(completed_dates or [today])).days + 1
        rate = len(completed_dates) / max(total_days, 1)
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "completion_rate": round(rate, 3),
            "total_checks": len(completed_dates),
            "dates": [d.isoformat() for d in sorted(completed_dates)],
        }

    def get_all_habits_stats(self, user_id: str) -> dict[str, dict]:
        habits = self.uow.habits.find_by_user(user_id)
        result: dict[str, dict] = {}
        today = date.today()
        for h in habits:
            logs = self.uow.habit_logs.find_by_habit_and_user(h.id or "", user_id)
            completed_dates = [log.log_date for log in logs if log.completed]
            current_streak, longest_streak = _compute_streak_dates(completed_dates, today)
            result[h.id or ""] = {
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "today_completed": today in completed_dates,
                "total_checks": len(completed_dates),
            }
        return result


def compute_all_log_dates(
    habit_logs: list[HabitLog],
) -> dict[str, list[date]]:
    by_habit: dict[str, list[date]] = defaultdict(list)
    for log in habit_logs:
        if log.completed:
            by_habit[log.habit_id].append(log.log_date)
    return dict(by_habit)
