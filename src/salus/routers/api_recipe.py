from fastapi import APIRouter, Depends, Query, Response

from salus.dependencies import get_current_user, get_recipe_service
from salus.models.user import User
from salus.schemas.food import (
    MealResponse,
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
)
from salus.services._helpers import uid
from salus.services.recipe import RecipeService

router = APIRouter(prefix="/api/v1/recipes")


@router.get("", response_model=list[RecipeResponse])
async def list_recipes(
    current_user: User = Depends(get_current_user),
    recipe_svc: RecipeService = Depends(get_recipe_service),
):
    recipes = recipe_svc.find_all(uid(current_user))
    result = []
    for r in recipes:
        result.append(recipe_svc.get(r.id or "", uid(current_user)))
    return result


@router.post("", response_model=RecipeResponse, status_code=201)
async def create_recipe(
    data: RecipeCreate,
    current_user: User = Depends(get_current_user),
    recipe_svc: RecipeService = Depends(get_recipe_service),
):
    return recipe_svc.create(data, uid(current_user))


@router.get("/{recipe_id}", response_model=RecipeResponse)
async def get_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    recipe_svc: RecipeService = Depends(get_recipe_service),
):
    return recipe_svc.get(recipe_id, uid(current_user))


@router.put("/{recipe_id}", response_model=RecipeResponse)
async def update_recipe(
    recipe_id: str,
    data: RecipeUpdate,
    current_user: User = Depends(get_current_user),
    recipe_svc: RecipeService = Depends(get_recipe_service),
):
    return recipe_svc.update(recipe_id, uid(current_user), data)


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    recipe_svc: RecipeService = Depends(get_recipe_service),
):
    recipe_svc.delete(recipe_id, uid(current_user))
    return Response(status_code=204)


@router.post("/{recipe_id}/cook", response_model=MealResponse)
async def cook_recipe(
    recipe_id: str,
    servings: float = Query(1.0, ge=0.25, le=10.0),
    current_user: User = Depends(get_current_user),
    recipe_svc: RecipeService = Depends(get_recipe_service),
):
    return recipe_svc.cook(recipe_id, uid(current_user), servings)
