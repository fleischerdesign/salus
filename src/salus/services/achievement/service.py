import logging
from datetime import datetime, timezone

from salus.models.achievement import AchievementDefinition, UserAchievement
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.achievement.evaluator import evaluate_achievement

logger = logging.getLogger("salus.services.achievement")


class AchievementService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def seed_definitions(self) -> int:
        from salus.services.achievement.definitions import ACHIEVEMENT_DEFINITIONS
        session = self.uow.session
        count = 0
        for ad in ACHIEVEMENT_DEFINITIONS:
            if session.get(AchievementDefinition, ad["code"]) is None:
                session.add(AchievementDefinition(
                    code=ad["code"],
                    title=ad["title"],
                    description=ad["description"],
                    icon=ad.get("icon", "emoji-events"),
                    tier=ad.get("tier", "bronze"),
                    category=ad.get("category", "tracking"),
                    condition_type=ad.get("condition_type", "count"),
                    condition_config=ad.get("condition_config", "{}"),
                    is_hidden=ad.get("is_hidden", False),
                    sort_order=ad.get("sort_order", 0),
                ))
                count += 1
        return count

    def get_all(self) -> list[AchievementDefinition]:
        return self.uow.achievement_definitions.find_all()

    def get_unlocked(self, user_id: str) -> list[UserAchievement]:
        return self.uow.user_achievements.find_by_user(user_id)

    def get_progress(
        self, user_id: str
    ) -> list[dict]:
        definitions = self.uow.achievement_definitions.find_all()
        unlocked_map = {
            ua.achievement_code: ua
            for ua in self.uow.user_achievements.find_by_user(user_id)
        }
        result: list[dict] = []
        for ad in definitions:
            ua = unlocked_map.get(ad.code)
            result.append({
                "code": ad.code,
                "title": ad.title,
                "description": ad.description,
                "icon": ad.icon,
                "tier": ad.tier.value if hasattr(ad.tier, "value") else ad.tier,
                "category": ad.category.value if hasattr(ad.category, "value") else ad.category,
                "is_hidden": ad.is_hidden,
                "sort_order": ad.sort_order,
                "unlocked_at": ua.unlocked_at.isoformat() if ua else None,
                "progress_current": ua.progress_current if ua else None,
                "progress_target": ua.progress_target if ua else None,
            })
        return result

    def evaluate(self, user_id: str) -> list[str]:
        definitions = self.uow.achievement_definitions.find_all()
        unlocked_map = {
            ua.achievement_code: ua
            for ua in self.uow.user_achievements.find_by_user(user_id)
        }
        newly_unlocked: list[str] = []

        for ad in definitions:
            if ad.code in unlocked_map:
                continue

            session = self.uow.session
            try:
                unlocked = evaluate_achievement(session, user_id, ad)
            except Exception:
                logger.exception("Error evaluating achievement %s for user %s", ad.code, user_id)
                continue

            if unlocked:
                ua = UserAchievement(
                    user_id=user_id,
                    achievement_code=ad.code,
                    unlocked_at=datetime.now(timezone.utc),
                )
                self.uow.user_achievements.create(ua)
                newly_unlocked.append(ad.code)
                logger.info("Achievement unlocked: %s for user %s", ad.code, user_id)

        return newly_unlocked
