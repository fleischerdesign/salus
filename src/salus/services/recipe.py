from salus.exceptions import NotFoundError
from salus.models.food import Recipe, RecipeIngredient
from salus.repositories.unit_of_work import IUnitOfWork


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
