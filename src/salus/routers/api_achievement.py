from fastapi import APIRouter, Depends

from salus.dependencies import get_achievement_service, get_current_user
from salus.models.user import User
from salus.schemas.achievement import (
    AchievementDefinitionResponse,
    AchievementWithProgress,
    AllStreaksResponse,
    UserAchievementResponse,
)
from salus.services._helpers import uid
from salus.services.achievement.service import AchievementService

router = APIRouter(prefix="/api/v1")


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
            achievement=AchievementDefinitionResponse(
                code=p["code"],
                title=p["title"],
                description=p["description"],
                icon=p["icon"],
                tier=p["tier"],
                category=p["category"],
                is_hidden=p["is_hidden"],
                sort_order=p["sort_order"],
            ),
            unlocked=UserAchievementResponse(
                id="",
                achievement_code=p["code"],
                unlocked_at=p["unlocked_at"],
                progress_current=p["progress_current"],
                progress_target=p["progress_target"],
                notified=False,
            ) if p["unlocked_at"] else None,
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
    ach_svc: AchievementService = Depends(get_achievement_service),
):
    return AllStreaksResponse(**ach_svc.get_streaks(uid(current_user)))
