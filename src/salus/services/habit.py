from datetime import date

from salus.exceptions import NotFoundError
from salus.models.habit import Habit, HabitLog
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.achievement.streak import compute_streak
from salus.services.timezone import user_today


def habit_streak_stats(
    uow: IUnitOfWork, habit_id: str, user_id: str, today: date
) -> dict:
    all_logs = uow.habit_logs.find_by_habit_and_user(habit_id, user_id)
    completed_dates = [log.log_date for log in all_logs if log.completed]
    current_streak, longest_streak = compute_streak(completed_dates, today)
    total_days = (today - min(completed_dates or [today])).days + 1
    rate = len(completed_dates) / max(total_days, 1)
    return {
        "completed_dates": completed_dates,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "completion_rate": round(rate, 3),
    }


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

    def _streak_stats(self, habit_id: str, user_id: str, today: date) -> dict:
        return habit_streak_stats(self.uow, habit_id, user_id, today)

    def get_logs(self, habit_id: str, user_id: str) -> list[HabitLog]:
        self.get(habit_id, user_id)
        return self.uow.habit_logs.find_by_habit_and_user(habit_id, user_id)

    def get_stats(self, habit_id: str, user_id: str) -> dict:
        self.get(habit_id, user_id)
        today = user_today(self.uow.session, user_id)
        stats = self._streak_stats(habit_id, user_id, today)
        completed_dates = stats["completed_dates"]
        return {
            "current_streak": stats["current_streak"],
            "longest_streak": stats["longest_streak"],
            "completion_rate": stats["completion_rate"],
            "total_checks": len(completed_dates),
            "dates": [d.isoformat() for d in sorted(completed_dates)],
        }

    def get_all_habits_stats(self, user_id: str) -> dict[str, dict]:
        habits = self.uow.habits.find_by_user(user_id)
        today = user_today(self.uow.session, user_id)
        completed_by_habit = self.uow.habit_logs.find_completed_dates_by_user(user_id)
        result: dict[str, dict] = {}
        for h in habits:
            habit_id = h.id or ""
            completed_dates = completed_by_habit.get(habit_id, [])
            current_streak, longest_streak = compute_streak(completed_dates, today)
            result[habit_id] = {
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "today_completed": today in completed_dates,
                "total_checks": len(completed_dates),
            }
        return result
