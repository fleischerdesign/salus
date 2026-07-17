import json
from datetime import date, datetime, timezone

from salus.exceptions import NotFoundError
from salus.models.food import (
    Meal,
    MealItem,
    Recipe,
    RecipeIngredient,
)
from salus.models.measurement import Measurement
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.food import RecipeCreate, RecipeUpdate


class RecipeService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def _get(self, recipe_id: str, user_id: str) -> Recipe:
        r = self.uow.recipes.get_by_id(recipe_id)
        if r is None or r.user_id != user_id:
            raise NotFoundError(f"Recipe {recipe_id} not found")
        return r

    def _resolve_food_items(self, ingredients: list[RecipeIngredient]) -> dict:
        food_ids = {ing.food_item_id for ing in ingredients}
        result = {}
        for fid in food_ids:
            food = self.uow.food_items.get_by_id(fid)
            if food:
                result[fid] = food
        return result

    def _calc_recipe_macros(
        self, ingredients: list[RecipeIngredient], food_map: dict
    ) -> dict:
        total = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
        for ing in ingredients:
            food = food_map.get(ing.food_item_id)
            if food is None:
                continue
            factor = ing.amount_g / food.serving_size if food.serving_size else 0
            total["calories"] += food.calories_per_serving * factor
            total["protein_g"] += food.protein_g * factor
            total["carbs_g"] += food.carbs_g * factor
            total["fat_g"] += food.fat_g * factor
        return total

    def _ingredients_to_response(
        self, ingredients: list[RecipeIngredient], food_map: dict
    ) -> list[dict]:
        result = []
        for ing in ingredients:
            food = food_map.get(ing.food_item_id)
            name = food.name if food else ""
            result.append({
                "id": ing.id,
                "food_item_id": ing.food_item_id,
                "food_item_name": name,
                "amount_g": ing.amount_g,
                "notes": ing.notes,
            })
        return result

    def _recipe_to_response(
        self, recipe: Recipe, ingredients: list[RecipeIngredient], food_map: dict
    ) -> dict:
        macros = self._calc_recipe_macros(ingredients, food_map)
        return {
            "id": recipe.id,
            "name": recipe.name,
            "description": recipe.description,
            "instructions": recipe.instructions,
            "servings": recipe.servings,
            "prep_time_min": recipe.prep_time_min,
            "cook_time_min": recipe.cook_time_min,
            "is_favorite": recipe.is_favorite,
            "ingredients": self._ingredients_to_response(ingredients, food_map),
            "total_calories": round(macros["calories"], 1),
            "total_protein_g": round(macros["protein_g"], 1),
            "total_carbs_g": round(macros["carbs_g"], 1),
            "total_fat_g": round(macros["fat_g"], 1),
            "created_at": recipe.created_at.isoformat() if recipe.created_at else "",
        }

    # ── CRUD ──

    def find_all(self, user_id: str) -> list[Recipe]:
        return self.uow.recipes.find_by_user(user_id)

    def get(self, recipe_id: str, user_id: str) -> dict:
        recipe = self._get(recipe_id, user_id)
        ingredients = self.uow.recipe_ingredients.find_by_recipe(recipe_id)
        food_map = self._resolve_food_items(ingredients)
        return self._recipe_to_response(recipe, ingredients, food_map)

    def create(self, data: RecipeCreate, user_id: str) -> dict:
        recipe = Recipe(
            user_id=user_id,
            name=data.name,
            description=data.description,
            instructions=data.instructions,
            servings=data.servings,
            prep_time_min=data.prep_time_min,
            cook_time_min=data.cook_time_min,
        )
        self.uow.recipes.create(recipe)

        ingredients = []
        for ing_data in data.ingredients:
            ing = RecipeIngredient(
                recipe_id=recipe.id or "",
                user_id=user_id,
                food_item_id=ing_data.food_item_id,
                amount_g=ing_data.amount_g,
                notes=ing_data.notes,
            )
            self.uow.recipe_ingredients.create(ing)
            ingredients.append(ing)

        food_map = self._resolve_food_items(ingredients)
        return self._recipe_to_response(recipe, ingredients, food_map)

    def update(self, recipe_id: str, user_id: str, data: RecipeUpdate) -> dict:
        recipe = self._get(recipe_id, user_id)

        if data.name is not None:
            recipe.name = data.name
        if data.description is not None:
            recipe.description = data.description
        if data.instructions is not None:
            recipe.instructions = data.instructions
        if data.servings is not None:
            recipe.servings = data.servings
        if data.prep_time_min is not None:
            recipe.prep_time_min = data.prep_time_min
        if data.cook_time_min is not None:
            recipe.cook_time_min = data.cook_time_min
        if data.is_favorite is not None:
            recipe.is_favorite = data.is_favorite
        self.uow.recipes.update(recipe)

        if data.ingredients is not None:
            old = self.uow.recipe_ingredients.find_by_recipe(recipe_id)
            for ing in old:
                self.uow.recipe_ingredients.delete(ing)

            ingredients = []
            for ing_data in data.ingredients:
                ing = RecipeIngredient(
                    recipe_id=recipe_id,
                    user_id=user_id,
                    food_item_id=ing_data.food_item_id,
                    amount_g=ing_data.amount_g,
                    notes=ing_data.notes,
                )
                self.uow.recipe_ingredients.create(ing)
                ingredients.append(ing)
        else:
            ingredients = self.uow.recipe_ingredients.find_by_recipe(recipe_id)

        food_map = self._resolve_food_items(ingredients)
        return self._recipe_to_response(recipe, ingredients, food_map)

    def delete(self, recipe_id: str, user_id: str) -> None:
        recipe = self._get(recipe_id, user_id)
        ingredients = self.uow.recipe_ingredients.find_by_recipe(recipe_id)
        for ing in ingredients:
            self.uow.recipe_ingredients.delete(ing)
        self.uow.recipes.delete(recipe)

    # ── Cook ──

    def cook(self, recipe_id: str, user_id: str, servings: float = 1.0) -> dict:
        recipe = self._get(recipe_id, user_id)
        recipe_ingredients = self.uow.recipe_ingredients.find_by_recipe(recipe_id)
        food_map = self._resolve_food_items(recipe_ingredients)

        scale = servings / recipe.servings if recipe.servings > 0 else 1.0

        meal = Meal(
            user_id=user_id,
            log_date=date.today(),
            meal_type="other",
            name=f"Recipe: {recipe.name}",
        )
        self.uow.meals.create(meal)

        meal_items = []
        for ing in recipe_ingredients:
            food = food_map.get(ing.food_item_id)
            if food:
                total_weight = ing.amount_g * scale
                mi = MealItem(
                    meal_id=meal.id or "",
                    user_id=user_id,
                    food_item_id=ing.food_item_id,
                    servings=total_weight / food.serving_size if food.serving_size else 0,
                    amount_g=total_weight,
                )
                self.uow.meal_items.create(mi)
                meal_items.append(mi)

        macros = self._calc_recipe_macros(recipe_ingredients, food_map)
        for k in macros:
            macros[k] *= scale

        measurement = Measurement(
            user_id=user_id,
            metric_code="nutrition",
            data_type="nutrition",
            source="meal",
            external_id=meal.id,
            value_json=json.dumps(macros),
            start_time=datetime.now(timezone.utc),
        )
        self.uow.measurements.create(measurement)

        return {
            "id": meal.id,
            "log_date": meal.log_date.isoformat(),
            "meal_type": meal.meal_type,
            "name": meal.name,
            "notes": meal.notes,
            "items": [
                {
                    "id": mi.id,
                    "food_item_id": mi.food_item_id,
                    "food_item_name": food_map.get(mi.food_item_id).name if food_map.get(mi.food_item_id) else "",
                    "servings": mi.servings,
                    "amount_g": mi.amount_g,
                    "calories": round((food_map.get(mi.food_item_id).calories_per_serving * mi.servings) if food_map.get(mi.food_item_id) else 0, 1),
                    "protein_g": round((food_map.get(mi.food_item_id).protein_g * mi.servings) if food_map.get(mi.food_item_id) else 0, 1),
                    "carbs_g": round((food_map.get(mi.food_item_id).carbs_g * mi.servings) if food_map.get(mi.food_item_id) else 0, 1),
                    "fat_g": round((food_map.get(mi.food_item_id).fat_g * mi.servings) if food_map.get(mi.food_item_id) else 0, 1),
                }
                for mi in meal_items
            ],
            "total_calories": round(macros["calories"], 1),
            "total_protein_g": round(macros["protein_g"], 1),
            "total_carbs_g": round(macros["carbs_g"], 1),
            "total_fat_g": round(macros["fat_g"], 1),
            "created_at": meal.created_at.isoformat() if meal.created_at else "",
        }
