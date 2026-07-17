from fastapi import APIRouter, Depends

from salus.dependencies import get_achievement_service, get_current_user
from salus.models.user import User
from salus.schemas.achievement import (
    AchievementWithProgress,
    AllStreaksResponse,
    StreakResponse,
    UserAchievementResponse,
)
from salus.services._helpers import uid
from salus.services.achievement.service import AchievementService
from salus.services.achievement.streak import compute_streak
from salus.repositories.unit_of_work import IUnitOfWork
from salus.dependencies import get_unit_of_work

router = APIRouter(prefix="/api/v1")


def _defn_to_response(ad) -> dict:
    return {
        "code": ad.code,
        "title": ad.title,
        "description": ad.description,
        "icon": ad.icon,
        "tier": ad.tier.value if hasattr(ad.tier, "value") else str(ad.tier),
        "category": ad.category.value if hasattr(ad.category, "value") else str(ad.category),
        "is_hidden": ad.is_hidden,
        "sort_order": ad.sort_order,
    }


def _unlocked_to_response(ua) -> dict:
    return {
        "id": ua.id,
        "achievement_code": ua.achievement_code,
        "unlocked_at": ua.unlocked_at.isoformat() if ua.unlocked_at else "",
        "progress_current": ua.progress_current,
        "progress_target": ua.progress_target,
        "notified": ua.notified,
    }


@router.get("/achievements", response_model=list[AchievementWithProgress])
async def list_achievements(
    current_user: User = Depends(get_current_user),
    ach_svc: AchievementService = Depends(get_achievement_service),
):
    progress = ach_svc.get_progress(uid(current_user))
    return [
        AchievementWithProgress(
            achievement={
                "code": p["code"],
                "title": p["title"],
                "description": p["description"],
                "icon": p["icon"],
                "tier": p["tier"],
                "category": p["category"],
                "is_hidden": p["is_hidden"],
                "sort_order": p["sort_order"],
            },
            unlocked={
                "id": "",
                "achievement_code": p["code"],
                "unlocked_at": p["unlocked_at"],
                "progress_current": p["progress_current"],
                "progress_target": p["progress_target"],
                "notified": False,
            } if p["unlocked_at"] else None,
        )
        for p in progress
        if not p.get("is_hidden") or p.get("unlocked_at")
    ]


@router.get("/achievements/unlocked", response_model=list[UserAchievementResponse])
async def list_unlocked(
    current_user: User = Depends(get_current_user),
    ach_svc: AchievementService = Depends(get_achievement_service),
):
    unlocked = ach_svc.get_unlocked(uid(current_user))
    return [_unlocked_to_response(ua) for ua in unlocked]


@router.get("/streaks", response_model=AllStreaksResponse)
async def get_all_streaks(
    current_user: User = Depends(get_current_user),
    uow: IUnitOfWork = Depends(get_unit_of_work),
    ach_svc: AchievementService = Depends(get_achievement_service),
):
    user_id = uid(current_user)
    from datetime import date
    today = date.today()

    from sqlmodel import select
    from salus.models.measurement import Measurement
    from salus.models.mood import MoodEntry
    from salus.models.workout import WorkoutSession

    session = uow.session

    meas_rows = session.exec(
        select(Measurement.start_time).where(
            Measurement.user_id == user_id,
            Measurement.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
    ).all()
    tracking_dates = [r.date() for r in meas_rows if hasattr(r, "date")]
    tr_current, tr_longest = compute_streak(tracking_dates, today)

    mood_rows = session.exec(
        select(MoodEntry.entry_date).where(
            MoodEntry.user_id == user_id,
            MoodEntry.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
    ).all()
    mood_dates = list(mood_rows)
    mo_current, mo_longest = compute_streak(mood_dates, today)

    workout_rows = session.exec(
        select(WorkoutSession.completed_at).where(
            WorkoutSession.user_id == user_id,
            WorkoutSession.completed_at.isnot(None),  # pyright: ignore[reportAttributeAccessIssue]
            WorkoutSession.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
    ).all()
    workout_dates = [r.date() for r in workout_rows if hasattr(r, "date")]
    wo_current, wo_longest = compute_streak(workout_dates, today)

    from salus.models.habit import Habit, HabitLog
    habits = session.exec(
        select(Habit).where(Habit.user_id == user_id, Habit.deleted_at.is_(None))  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
    ).all()
    habit_streaks: dict[str, dict] = {}
    for h in habits:
        logs = session.exec(
            select(HabitLog.log_date).where(
                HabitLog.habit_id == h.id,
                HabitLog.completed == True,  # noqa: E712
                HabitLog.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
            )
        ).all()
        hc, hl = compute_streak(list(logs), today)
        habit_streaks[h.id or ""] = {"current": hc, "longest": hl, "total_entries": len(list(logs))}

    return AllStreaksResponse(
        tracking=StreakResponse(current=tr_current, longest=tr_longest, total_entries=len(tracking_dates)),
        mood=StreakResponse(current=mo_current, longest=mo_longest, total_entries=len(mood_dates)),
        habits=habit_streaks,
        workout=StreakResponse(current=wo_current, longest=wo_longest, total_entries=len(workout_dates)),
    )
