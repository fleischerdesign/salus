"""Typed payloads for domain-verb command handlers.

Command handlers are the single source of truth for domain writes. Their
payloads are validated here (once), and both transports build them: the
sync-push pipeline from raw JSON, and the REST routers from their request
models. This keeps validation in exactly one place per command.
"""
from pydantic import BaseModel, Field


class MealItemPayload(BaseModel):
    id: str | None = None
    food_item_id: str
    servings: float = Field(default=1.0, gt=0)
    amount_g: float | None = None


class CreateMealPayload(BaseModel):
    id: str | None = None
    log_date: str | None = None
    meal_type: str = "snack"
    name: str | None = None
    notes: str | None = None
    measurement_id: str | None = None
    items: list[MealItemPayload]


class UpdateMealPayload(BaseModel):
    id: str
    meal_type: str | None = None
    name: str | None = None
    notes: str | None = None
    measurement_id: str | None = None
    items: list[MealItemPayload] | None = None


class DeleteMealPayload(BaseModel):
    id: str


class RecipeIngredientPayload(BaseModel):
    id: str | None = None
    food_item_id: str
    amount_g: float
    notes: str | None = None


class CreateRecipePayload(BaseModel):
    id: str | None = None
    name: str
    description: str | None = None
    instructions: str | None = None
    servings: int = Field(default=4, gt=0)
    prep_time_min: int | None = None
    cook_time_min: int | None = None
    is_favorite: bool = False
    ingredients: list[RecipeIngredientPayload]


class UpdateRecipePayload(BaseModel):
    id: str
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    servings: int | None = None
    prep_time_min: int | None = None
    cook_time_min: int | None = None
    is_favorite: bool | None = None
    ingredients: list[RecipeIngredientPayload] | None = None


class DeleteRecipePayload(BaseModel):
    id: str


class CookRecipePayload(BaseModel):
    recipe_id: str
    servings: float = Field(default=1.0, gt=0)
    measurement_id: str | None = None


class ToggleHabitCheckPayload(BaseModel):
    habit_id: str


class LogMedicationPayload(BaseModel):
    id: str | None = None
    medication_id: str
    schedule_id: str | None = None
    taken_at: str | None = None
    dosage_taken: str | None = None
    skipped: bool = False
    notes: str | None = None


class SkipMedicationDosePayload(BaseModel):
    id: str | None = None
    medication_id: str
    schedule_id: str
    scheduled_time: str


class DeleteMedicationLogPayload(BaseModel):
    id: str
