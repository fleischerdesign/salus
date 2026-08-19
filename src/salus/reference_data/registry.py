"""Central registry of all reference data specifications."""

from typing import Any

from salus.models.achievement import AchievementDefinition
from salus.models.food import FoodItem
from salus.models.lab import LabMarker
from salus.models.metric_definition import MetricDefinition, MetricGroup
from salus.models.mood import MoodTag, MoodTagCategory
from salus.models.workout import Exercise
from salus.reference_data.definitions.achievements import ACHIEVEMENT_DEFINITIONS
from salus.reference_data.definitions.exercises import COMMON_EXERCISES
from salus.reference_data.definitions.foods import COMMON_FOODS
from salus.reference_data.definitions.lab_markers import LAB_MARKERS
from salus.reference_data.definitions.metrics import METRIC_DEFINITIONS, METRIC_GROUPS
from salus.reference_data.definitions.mood_tags import DEFAULT_MOOD_TAGS
from salus.reference_data.types import ReferenceSpec
from salus.services.constants import SOURCE_SYSTEM


def _instantiate_mood_tag(d: dict[str, Any]) -> MoodTag:
    return MoodTag(
        code=d["code"],
        label=d["label"],
        emoji=d["emoji"],
        category=MoodTagCategory(d["category"]),
        is_system=True,
    )


def _instantiate_food_item(d: dict[str, Any]) -> FoodItem:
    return FoodItem(
        id=d["id"],
        name=d["name"],
        serving_size=d.get("serving_size", 100),
        serving_unit="g",
        calories_per_serving=d.get("calories_per_serving", 0),
        protein_g=d.get("protein_g", 0),
        carbs_g=d.get("carbs_g", 0),
        fat_g=d.get("fat_g", 0),
        fiber_g=d.get("fiber_g"),
        sugar_g=d.get("sugar_g"),
        saturated_fat_g=d.get("saturated_fat_g"),
        sodium_mg=d.get("sodium_mg"),
        is_verified=True,
        user_id=None,
        source=SOURCE_SYSTEM,
    )


def _instantiate_exercise(d: dict[str, Any]) -> Exercise:
    return Exercise(
        id=d["id"],
        name=d["name"],
        equipment=d.get("equipment", "barbell"),
        primary_muscles=d["primary_muscles"],
        secondary_muscles=d.get("secondary_muscles"),
        description=d.get("description"),
        instructions=d.get("instructions"),
        suggested_rest_seconds=d.get("suggested_rest_seconds", 120),
        user_id=None,
    )


REFERENCE_SPECS: tuple[ReferenceSpec, ...] = (
    ReferenceSpec(
        name="metric_groups",
        model=MetricGroup,
        unique_key="key",
        items=METRIC_GROUPS,
        update_fields=("name", "icon", "input_mode"),
    ),
    ReferenceSpec(
        name="metric_definitions",
        model=MetricDefinition,
        unique_key="code",
        items=METRIC_DEFINITIONS,
        update_fields=(
            "source_data_type",
            "group_key",
            "unit",
            "name",
            "sort_order",
            "min_value",
            "max_value",
        ),
    ),
    ReferenceSpec(
        name="achievement_definitions",
        model=AchievementDefinition,
        unique_key="code",
        items=ACHIEVEMENT_DEFINITIONS,
        update_fields=(
            "title",
            "description",
            "icon",
            "tier",
            "category",
            "condition_type",
            "condition_config",
            "is_hidden",
            "sort_order",
        ),
    ),
    ReferenceSpec(
        name="mood_tags",
        model=MoodTag,
        unique_key="code",
        items=DEFAULT_MOOD_TAGS,
        update_fields=("label", "emoji", "category", "is_system"),
        instantiator=_instantiate_mood_tag,
    ),
    ReferenceSpec(
        name="lab_markers",
        model=LabMarker,
        unique_key="code",
        items=LAB_MARKERS,
        update_fields=(
            "category",
            "reference_low",
            "reference_high",
            "optimal_low",
            "optimal_high",
            "description",
        ),
    ),
    ReferenceSpec(
        name="common_foods",
        model=FoodItem,
        unique_key="id",
        items=COMMON_FOODS,
        update_fields=(
            "name",
            "serving_size",
            "serving_unit",
            "calories_per_serving",
            "protein_g",
            "carbs_g",
            "fat_g",
            "fiber_g",
            "sugar_g",
            "saturated_fat_g",
            "sodium_mg",
        ),
        instantiator=_instantiate_food_item,
    ),
    ReferenceSpec(
        name="common_exercises",
        model=Exercise,
        unique_key="id",
        items=COMMON_EXERCISES,
        update_fields=(
            "name",
            "equipment",
            "primary_muscles",
            "secondary_muscles",
            "description",
            "instructions",
            "suggested_rest_seconds",
        ),
        instantiator=_instantiate_exercise,
    ),
)
