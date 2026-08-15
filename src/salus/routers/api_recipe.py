from fastapi import APIRouter, Depends, Query, Response

from salus.dependencies import (
    get_current_user,
    get_meal_service,
    get_recipe_service,
    get_write_pipeline,
)
from salus.exceptions import raise_from_command_result
from salus.models.user import User
from salus.schemas.food import (
    MealResponse,
    RecipeCreate,
    RecipeResponse,
    RecipeUpdate,
)
from salus.schemas.sync import SyncOperation
from salus.services._helpers import uid
from salus.services.meal import MealService
from salus.services.recipe import RecipeService
from salus.services.write_pipeline import WritePipeline

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
    pipeline: WritePipeline = Depends(get_write_pipeline),
    recipe_svc: RecipeService = Depends(get_recipe_service),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="create_recipe", payload=data.model_dump())]
    )[0]
    raise_from_command_result(result.status, result.message)
    return recipe_svc.get(result.id or "", uid(current_user))


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
    pipeline: WritePipeline = Depends(get_write_pipeline),
    recipe_svc: RecipeService = Depends(get_recipe_service),
):
    result = pipeline.process(
        [
            SyncOperation(
                type="command",
                command="update_recipe",
                payload={**data.model_dump(), "id": recipe_id},
            )
        ]
    )[0]
    raise_from_command_result(result.status, result.message)
    return recipe_svc.get(recipe_id, uid(current_user))


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="delete_recipe", payload={"id": recipe_id})]
    )[0]
    raise_from_command_result(result.status, result.message)
    return Response(status_code=204)


@router.post("/{recipe_id}/cook", response_model=MealResponse)
async def cook_recipe(
    recipe_id: str,
    servings: float = Query(1.0, ge=0.25, le=10.0),
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    meal_svc: MealService = Depends(get_meal_service),
):
    result = pipeline.process(
        [
            SyncOperation(
                type="command",
                command="cook_recipe",
                payload={"recipe_id": recipe_id, "servings": servings},
            )
        ]
    )[0]
    raise_from_command_result(result.status, result.message)
    return meal_svc.get(result.id or "", uid(current_user))
