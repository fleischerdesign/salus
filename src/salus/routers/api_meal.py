from datetime import date

from fastapi import APIRouter, Depends, Query, Response

from salus.dependencies import (
    get_current_user,
    get_meal_service,
    get_write_pipeline,
)
from salus.exceptions import raise_from_command_result
from salus.models.user import User
from salus.schemas.food import (
    MealCreate,
    MealResponse,
    MealSummaryResponse,
    MealUpdate,
)
from salus.schemas.sync import SyncOperation
from salus.services._helpers import uid
from salus.services.meal import MealService
from salus.services.write_pipeline import WritePipeline

router = APIRouter(prefix="/api/v1/meals")


@router.get("", response_model=list[MealResponse])
async def list_meals(
    since: str | None = Query(None),
    until: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    meal_svc: MealService = Depends(get_meal_service),
):
    _since = date.fromisoformat(since) if since else None
    _until = date.fromisoformat(until) if until else None
    return meal_svc.find_by_date(uid(current_user), _since, _until)


@router.post("", response_model=MealResponse, status_code=201)
async def create_meal(
    data: MealCreate,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    meal_svc: MealService = Depends(get_meal_service),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="create_meal", payload=data.model_dump())]
    )[0]
    raise_from_command_result(result.status, result.message)
    return meal_svc.get(result.id or "", uid(current_user))


@router.get("/today", response_model=list[MealResponse])
async def get_today(
    current_user: User = Depends(get_current_user),
    meal_svc: MealService = Depends(get_meal_service),
):
    return meal_svc.get_today(uid(current_user))


@router.get("/summary", response_model=list[MealSummaryResponse])
async def get_summary(
    since: str | None = Query(None),
    until: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    meal_svc: MealService = Depends(get_meal_service),
):
    _since = date.fromisoformat(since) if since else None
    _until = date.fromisoformat(until) if until else None
    return meal_svc.get_summary(uid(current_user), _since, _until)


@router.get("/{meal_id}", response_model=MealResponse)
async def get_meal(
    meal_id: str,
    current_user: User = Depends(get_current_user),
    meal_svc: MealService = Depends(get_meal_service),
):
    return meal_svc.get(meal_id, uid(current_user))


@router.put("/{meal_id}", response_model=MealResponse)
async def update_meal(
    meal_id: str,
    data: MealUpdate,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
    meal_svc: MealService = Depends(get_meal_service),
):
    result = pipeline.process(
        [
            SyncOperation(
                type="command",
                command="update_meal",
                payload={**data.model_dump(), "id": meal_id},
            )
        ]
    )[0]
    raise_from_command_result(result.status, result.message)
    return meal_svc.get(meal_id, uid(current_user))


@router.delete("/{meal_id}", status_code=204)
async def delete_meal(
    meal_id: str,
    current_user: User = Depends(get_current_user),
    pipeline: WritePipeline = Depends(get_write_pipeline),
):
    result = pipeline.process(
        [SyncOperation(type="command", command="delete_meal", payload={"id": meal_id})]
    )[0]
    raise_from_command_result(result.status, result.message)
    return Response(status_code=204)
