from datetime import date, datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from salus.services._helpers import uuid7_str

if TYPE_CHECKING:
    from salus.models.user import User  # noqa: F401


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    OTHER = "other"


class FoodItem(SQLModel, table=True):
    __tablename__ = "food_item"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    name: str
    brand: str | None = Field(default=None)
    barcode: str | None = Field(default=None, index=True)
    serving_size: float = Field(default=100.0)
    serving_unit: str = Field(default="g")
    calories_per_serving: float = Field(default=0.0)
    protein_g: float = Field(default=0.0)
    carbs_g: float = Field(default=0.0)
    fat_g: float = Field(default=0.0)
    fiber_g: float | None = Field(default=None)
    sugar_g: float | None = Field(default=None)
    saturated_fat_g: float | None = Field(default=None)
    sodium_mg: float | None = Field(default=None)
    is_verified: bool = Field(default=False)
    user_id: str | None = Field(default=None, foreign_key="user.id")
    source: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)


class Meal(SQLModel, table=True):
    __tablename__ = "meal"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    log_date: date
    meal_type: str = Field(default="snack")
    name: str | None = Field(default=None)
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    user: "User" = Relationship()


class MealItem(SQLModel, table=True):
    __tablename__ = "meal_item"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    meal_id: str = Field(foreign_key="meal.id")
    user_id: str = Field(foreign_key="user.id")
    food_item_id: str = Field(foreign_key="food_item.id")
    servings: float = Field(default=1.0)
    amount_g: float | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = Field(default=None)

    meal: "Meal" = Relationship()
    food_item: "FoodItem" = Relationship()


class Recipe(SQLModel, table=True):
    __tablename__ = "recipe"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    user_id: str = Field(foreign_key="user.id")
    name: str
    description: str | None = Field(default=None)
    instructions: str | None = Field(default=None)
    servings: int = Field(default=4)
    prep_time_min: int | None = Field(default=None)
    cook_time_min: int | None = Field(default=None)
    is_favorite: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(
        default=None,
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )
    deleted_at: datetime | None = Field(default=None)

    user: "User" = Relationship()


class RecipeIngredient(SQLModel, table=True):
    __tablename__ = "recipe_ingredient"  # pyright: ignore[reportAssignmentType]

    id: str | None = Field(default_factory=uuid7_str, primary_key=True)
    recipe_id: str = Field(foreign_key="recipe.id")
    user_id: str = Field(foreign_key="user.id")
    food_item_id: str = Field(foreign_key="food_item.id")
    amount_g: float
    notes: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = Field(default=None)

    recipe: "Recipe" = Relationship()
    food_item: "FoodItem" = Relationship()
