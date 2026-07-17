from sqlmodel import select

from salus.models.achievement import AchievementDefinition, UserAchievement
from salus.repositories.base import Repository


class AchievementDefinitionRepository(Repository[AchievementDefinition]):
    model = AchievementDefinition

    def find_all(self) -> list[AchievementDefinition]:
        return list(
            self.session.exec(
                select(AchievementDefinition).order_by(AchievementDefinition.sort_order)  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_code(self, code: str) -> AchievementDefinition | None:
        return self.session.get(AchievementDefinition, code)

    def find_by_category(self, category: str) -> list[AchievementDefinition]:
        return list(
            self.session.exec(
                select(AchievementDefinition).where(
                    AchievementDefinition.category == category  # pyright: ignore[reportAttributeAccessIssue]
                ).order_by(AchievementDefinition.sort_order)  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )


class UserAchievementRepository(Repository[UserAchievement]):
    model = UserAchievement

    def find_by_user(self, user_id: str) -> list[UserAchievement]:
        return list(
            self.session.exec(
                select(UserAchievement).where(
                    UserAchievement.user_id == user_id
                ).order_by(UserAchievement.unlocked_at.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_user_and_code(
        self, user_id: str, achievement_code: str
    ) -> UserAchievement | None:
        stmt = select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_code == achievement_code,
        )
        return self.session.exec(stmt).first()
