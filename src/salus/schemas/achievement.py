from pydantic import BaseModel


class AchievementDefinitionResponse(BaseModel):
    code: str
    title: str
    description: str
    icon: str
    tier: str
    category: str
    is_hidden: bool
    sort_order: int


class UserAchievementResponse(BaseModel):
    id: str
    achievement_code: str
    unlocked_at: str
    progress_current: float | None = None
    progress_target: float | None = None
    notified: bool


class AchievementWithProgress(BaseModel):
    achievement: AchievementDefinitionResponse
    unlocked: UserAchievementResponse | None = None


class StreakResponse(BaseModel):
    current: int
    longest: int
    total_entries: int


class AllStreaksResponse(BaseModel):
    tracking: StreakResponse
    mood: StreakResponse
    habits: dict[str, StreakResponse]
    workout: StreakResponse
