from __future__ import annotations

from typing import Any, TYPE_CHECKING

from salus.models.food import Recipe, RecipeIngredient
from salus.schemas.commands import (
    CookRecipePayload,
    CreateMealPayload,
    CreateRecipePayload,
    DeleteRecipePayload,
    MealItemPayload,
    UpdateRecipePayload,
)
from salus.services._helpers import uid
from salus.services.command_registry import CommandResult, register
from salus.services.commands.meal import CreateMealHandler
from salus.services.serialization import serialize_record
from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User

_RECIPE_FIELDS = (
    "id", "user_id", "name", "description", "instructions", "servings",
    "prep_time_min", "cook_time_min", "is_favorite",
    "created_at", "updated_at", "deleted_at",
)


@register("create_recipe")
class CreateRecipeHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = CreateRecipePayload.model_validate(payload)
        user_id = uid(user)
        recipe = Recipe(
            id=data.id or uuid7_str(),
            user_id=user_id,
            name=data.name,
            description=data.description,
            instructions=data.instructions,
            servings=data.servings,
            prep_time_min=data.prep_time_min,
            cook_time_min=data.cook_time_min,
            is_favorite=data.is_favorite,
        )
        uow.recipes.add(recipe)

        for ing_data in data.ingredients:
            uow.recipe_ingredients.add(RecipeIngredient(
                id=ing_data.id or uuid7_str(),
                recipe_id=recipe.id or "",
                user_id=user_id,
                food_item_id=ing_data.food_item_id,
                amount_g=ing_data.amount_g,
                notes=ing_data.notes,
            ))

        uow.commit()
        uow.session.refresh(recipe)
        return CommandResult(
            status="created",
            id=recipe.id,
            record=serialize_record(recipe, list(_RECIPE_FIELDS)),
        )


@register("update_recipe")
class UpdateRecipeHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = UpdateRecipePayload.model_validate(payload)
        user_id = uid(user)
        recipe = uow.recipes.get_by_id(data.id)
        if not recipe or recipe.user_id != user_id:
            return CommandResult(status="not_found", message="Recipe not found")

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
        uow.recipes.add(recipe)

        if data.ingredients is not None:
            for old in uow.recipe_ingredients.find_by_recipe(data.id):
                uow.recipe_ingredients.delete(old)
            for ing_data in data.ingredients:
                uow.recipe_ingredients.add(RecipeIngredient(
                    id=ing_data.id or uuid7_str(),
                    recipe_id=data.id,
                    user_id=user_id,
                    food_item_id=ing_data.food_item_id,
                    amount_g=ing_data.amount_g,
                    notes=ing_data.notes,
                ))

        uow.commit()
        uow.session.refresh(recipe)
        return CommandResult(
            status="updated",
            id=recipe.id,
            record=serialize_record(recipe, list(_RECIPE_FIELDS)),
        )


@register("delete_recipe")
class DeleteRecipeHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = DeleteRecipePayload.model_validate(payload)
        recipe = uow.recipes.get_by_id(data.id)
        if not recipe:
            return CommandResult(status="deleted", id=data.id)
        if recipe.user_id != uid(user):
            return CommandResult(status="forbidden", message="Not your recipe")

        for ing in uow.recipe_ingredients.find_by_recipe(data.id):
            uow.recipe_ingredients.delete(ing)
        uow.recipes.delete(recipe)
        uow.commit()
        return CommandResult(status="deleted", id=data.id)


@register("cook_recipe")
class CookRecipeHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = CookRecipePayload.model_validate(payload)
        recipe = uow.recipes.get_by_id(data.recipe_id)
        if not recipe:
            return CommandResult(status="not_found", message="Recipe not found")
        if recipe.user_id != uid(user):
            return CommandResult(status="forbidden", message="Not your recipe")

        items = data.items
        if not items:
            ingredients = uow.recipe_ingredients.find_by_recipe(data.recipe_id)
            food_map = _resolve_food_items(uow, ingredients)
            scale = data.servings / recipe.servings if recipe.servings > 0 else 1.0
            items = []
            for ing in ingredients:
                food = food_map.get(ing.food_item_id)
                if food is None:
                    continue
                total_weight = round(ing.amount_g * scale)
                items.append(MealItemPayload(
                    id=uuid7_str(),
                    food_item_id=ing.food_item_id,
                    servings=total_weight / food.serving_size if food.serving_size else 0,
                    amount_g=total_weight,
                ))

        meal_payload = CreateMealPayload(
            id=data.meal_id,
            meal_type="other",
            name=f"Recipe: {recipe.name}",
            measurement_id=data.measurement_id,
            items=items,
        )
        return CreateMealHandler().execute(uow, user, meal_payload.model_dump())


def _resolve_food_items(uow: IUnitOfWork, ingredients: list[RecipeIngredient]) -> dict:
    food_ids = {ing.food_item_id for ing in ingredients}
    result: dict = {}
    for fid in food_ids:
        food = uow.food_items.get_by_id(fid)
        if food:
            result[fid] = food
    return result
