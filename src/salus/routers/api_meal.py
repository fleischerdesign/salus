from datetime import date

from fastapi import APIRouter, Depends, Query, Response

from salus.dependencies import get_current_user, get_meal_service
from salus.models.user import User
from salus.schemas.food import (
    MealCreate,
    MealResponse,
    MealSummaryResponse,
    MealUpdate,
)
from salus.services._helpers import uid
from salus.services.meal import MealService

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
    meal_svc: MealService = Depends(get_meal_service),
):
    return meal_svc.create(data, uid(current_user))


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
    meal_svc: MealService = Depends(get_meal_service),
):
    return meal_svc.update(meal_id, uid(current_user), data)


@router.delete("/{meal_id}", status_code=204)
async def delete_meal(
    meal_id: str,
    current_user: User = Depends(get_current_user),
    meal_svc: MealService = Depends(get_meal_service),
):
    meal_svc.delete(meal_id, uid(current_user))
    return Response(status_code=204)
