from pydantic import BaseModel, Field


# ── FoodItem ──


class FoodItemCreate(BaseModel):
    name: str
    brand: str | None = None
    barcode: str | None = None
    serving_size: float = Field(default=100.0)
    serving_unit: str = Field(default="g")
    calories_per_serving: float = Field(default=0.0)
    protein_g: float = Field(default=0.0)
    carbs_g: float = Field(default=0.0)
    fat_g: float = Field(default=0.0)
    fiber_g: float | None = None
    sugar_g: float | None = None
    saturated_fat_g: float | None = None
    sodium_mg: float | None = None


class FoodItemResponse(BaseModel):
    id: str
    name: str
    brand: str | None = None
    barcode: str | None = None
    serving_size: float
    serving_unit: str
    calories_per_serving: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float | None = None
    sugar_g: float | None = None
    saturated_fat_g: float | None = None
    sodium_mg: float | None = None
    is_verified: bool
    source: str | None = None
    created_at: str


class FoodItemSearchResponse(BaseModel):
    items: list[FoodItemResponse]


# ── Meal ──


class MealItemCreate(BaseModel):
    food_item_id: str
    servings: float = Field(default=1.0, gt=0)
    amount_g: float | None = None


class MealCreate(BaseModel):
    log_date: str | None = None
    meal_type: str = Field(default="snack")
    name: str | None = None
    notes: str | None = None
    items: list[MealItemCreate]


class MealItemResponse(BaseModel):
    id: str
    food_item_id: str
    food_item_name: str = ""
    servings: float
    amount_g: float | None = None
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0


class MealResponse(BaseModel):
    id: str
    log_date: str
    meal_type: str
    name: str | None = None
    notes: str | None = None
    items: list[MealItemResponse]
    total_calories: float = 0.0
    total_protein_g: float = 0.0
    total_carbs_g: float = 0.0
    total_fat_g: float = 0.0
    created_at: str


class MealUpdate(BaseModel):
    meal_type: str | None = None
    name: str | None = None
    notes: str | None = None
    items: list[MealItemCreate] | None = None


class MealSummaryResponse(BaseModel):
    date: str
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    meal_count: int


# ── Recipe ──


class RecipeIngredientCreate(BaseModel):
    food_item_id: str
    amount_g: float
    notes: str | None = None


class RecipeCreate(BaseModel):
    name: str
    description: str | None = None
    instructions: str | None = None
    servings: int = Field(default=4, gt=0)
    prep_time_min: int | None = None
    cook_time_min: int | None = None
    ingredients: list[RecipeIngredientCreate]


class RecipeIngredientResponse(BaseModel):
    id: str
    food_item_id: str
    food_item_name: str = ""
    amount_g: float
    notes: str | None = None


class RecipeResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    instructions: str | None = None
    servings: int
    prep_time_min: int | None = None
    cook_time_min: int | None = None
    is_favorite: bool
    ingredients: list[RecipeIngredientResponse]
    total_calories: float = 0.0
    total_protein_g: float = 0.0
    total_carbs_g: float = 0.0
    total_fat_g: float = 0.0
    created_at: str


class RecipeUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    instructions: str | None = None
    servings: int | None = None
    prep_time_min: int | None = None
    cook_time_min: int | None = None
    is_favorite: bool | None = None
    ingredients: list[RecipeIngredientCreate] | None = None
