from collections import Counter
from datetime import date, timedelta

from salus.models.mood import MoodEntry, MoodTag, MoodTagCategory
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.achievement.streak import compute_streak
from salus.services.analytics.stats import linear_regression
from salus.services.timezone import user_today

DEFAULT_MOOD_TAGS: list[dict[str, str]] = [
    {"code": "energetic", "label": "Energetic", "emoji": "⚡", "category": "positive"},
    {"code": "happy", "label": "Happy", "emoji": "😊", "category": "positive"},
    {"code": "productive", "label": "Productive", "emoji": "✅", "category": "positive"},
    {"code": "grateful", "label": "Grateful", "emoji": "🙏", "category": "positive"},
    {"code": "calm", "label": "Calm", "emoji": "🧘", "category": "positive"},
    {"code": "okay", "label": "Okay", "emoji": "😐", "category": "neutral"},
    {"code": "tired", "label": "Tired", "emoji": "😴", "category": "negative"},
    {"code": "stressed", "label": "Stressed", "emoji": "😰", "category": "negative"},
    {"code": "anxious", "label": "Anxious", "emoji": "😟", "category": "negative"},
    {"code": "sad", "label": "Sad", "emoji": "😢", "category": "negative"},
    {"code": "frustrated", "label": "Frustrated", "emoji": "😤", "category": "negative"},
    {"code": "sick", "label": "Sick", "emoji": "🤒", "category": "negative"},
]


class MoodService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def seed_tags(self) -> int:
        session = self.uow.session
        count = 0
        for d in DEFAULT_MOOD_TAGS:
            if session.get(MoodTag, d["code"]) is None:
                session.add(MoodTag(
                    code=d["code"],
                    label=d["label"],
                    emoji=d["emoji"],
                    category=MoodTagCategory(d["category"]),
                    is_system=True,
                ))
                count += 1
        return count

    def get_tags(self) -> list[MoodTag]:
        return self.uow.mood_tags.find_all_tags()

    def find_by_user_range(
        self, user_id: str, since: date | None = None, until: date | None = None
    ) -> list[MoodEntry]:
        if since is None or until is None:
            return self.uow.mood_entries.find_by_user(user_id)
        return self.uow.mood_entries.find_by_user_range(user_id, since, until)

    def get_by_date(self, user_id: str, entry_date: date) -> MoodEntry | None:
        return self.uow.mood_entries.find_by_user_and_date(user_id, entry_date)

    def get_stats(
        self, user_id: str, days: int = 30
    ) -> dict:
        today = user_today(self.uow.session, user_id)
        since = today - timedelta(days=days)
        entries = self.uow.mood_entries.find_by_user_range(user_id, since, today)

        if not entries:
            return {
                "average": 0,
                "mode": None,
                "trend_slope": None,
                "min_score": 0,
                "max_score": 0,
                "total_entries": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "distribution": {},
            }

        scores = [e.mood_score for e in entries]

        freq = Counter(scores)
        mode = freq.most_common(1)[0][0] if freq else None

        avg = sum(scores) / len(scores)

        trend: float | None = None
        if len(scores) >= 5:
            xs = [float(i) for i in range(len(scores))]
            reg = linear_regression(xs, [float(s) for s in scores])
            if reg:
                trend = round(reg.slope, 4)

        unique_dates = sorted(
            set(_e.entry_date for _e in entries), reverse=True
        )
        current_streak, longest_streak = compute_streak(unique_dates, today)

        dist: dict[str, int] = {}
        for s in range(1, 11):
            count = freq.get(s, 0)
            if count > 0:
                dist[str(s)] = count

        return {
            "average": round(avg, 2),
            "mode": mode,
            "trend_slope": trend,
            "min_score": min(scores),
            "max_score": max(scores),
            "total_entries": len(entries),
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "distribution": dist,
        }
