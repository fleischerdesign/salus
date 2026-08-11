from enum import Enum


class DataType(str, Enum):
    NUMBER = "number"
    TEXT = "text"
    BOOLEAN = "boolean"


from salus.models.achievement import AchievementDefinition, UserAchievement  # noqa: F401, E402
from salus.models.api_token import ApiToken  # noqa: F401, E402
from salus.models.asymmetric_share import AsymmetricShare, ShareRecipient  # noqa: F401, E402
from salus.models.circadian import CircadianProfile  # noqa: F401, E402
from salus.models.dashboard import DashboardWidget  # noqa: F401, E402
from salus.models.food import FoodItem, Meal, MealItem, Recipe, RecipeIngredient  # noqa: F401, E402
from salus.models.goal import Goal  # noqa: F401, E402
from salus.models.habit import Habit, HabitLog  # noqa: F401, E402
from salus.models.insight import Insight  # noqa: F401, E402
from salus.models.journal import JournalEntry  # noqa: F401, E402
from salus.models.measurement import Measurement  # noqa: F401, E402
from salus.models.medication import (  # noqa: F401, E402
    Medication,
    MedicationInventory,
    MedicationLog,
    MedicationSchedule,
)
from salus.models.metric_definition import MetricDefinition, MetricGroup  # noqa: F401, E402
from salus.models.metric_preference import UserMetricPreference  # noqa: F401, E402
from salus.models.mood import MoodEntry, MoodTag  # noqa: F401, E402
from salus.models.notification import Notification  # noqa: F401, E402
from salus.models.sharing import (  # noqa: F401, E402
    FederatedAccessLog,
    FederatedMeasurementCache,
    LeaderboardGroup,
    LeaderboardMember,
    SharingRelationship,
)
from salus.models.sync_push_log import SyncPushLog  # noqa: F401, E402
from salus.models.system_config import SystemConfig  # noqa: F401, E402
from salus.models.user import User  # noqa: F401, E402
from salus.models.user_identity import UserIdentity  # noqa: F401, E402
from salus.models.user_source_preference import UserSourcePreference  # noqa: F401, E402
from salus.models.workout import (  # noqa: F401, E402
    Exercise,
    WorkoutLogEntry,
    WorkoutPlan,
    WorkoutPlanExercise,
    WorkoutSession,
)
