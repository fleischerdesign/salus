from fastapi import APIRouter, Depends, Query

from salus.dependencies import get_current_user, get_food_item_service
from salus.models.user import User
from salus.schemas.food import FoodItemCreate, FoodItemResponse, FoodItemSearchResponse
from salus.services._helpers import uid
from salus.services.food_item import FoodItemService

router = APIRouter(prefix="/api/v1/food")


def _food_item_to_response(item) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "brand": item.brand,
        "barcode": item.barcode,
        "serving_size": item.serving_size,
        "serving_unit": item.serving_unit,
        "calories_per_serving": item.calories_per_serving,
        "protein_g": item.protein_g,
        "carbs_g": item.carbs_g,
        "fat_g": item.fat_g,
        "fiber_g": item.fiber_g,
        "sugar_g": item.sugar_g,
        "saturated_fat_g": item.saturated_fat_g,
        "sodium_mg": item.sodium_mg,
        "is_verified": item.is_verified,
        "source": item.source,
        "created_at": item.created_at.isoformat() if item.created_at else "",
    }


@router.get("/items/search", response_model=FoodItemSearchResponse)
async def search_food(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    food_svc: FoodItemService = Depends(get_food_item_service),
):
    results = food_svc.search(q, limit)
    return {"items": [_food_item_to_response(r) for r in results]}


@router.get("/items/barcode/{barcode}")
async def lookup_barcode(
    barcode: str,
    current_user: User = Depends(get_current_user),
    food_svc: FoodItemService = Depends(get_food_item_service),
):
    item = food_svc.find_by_barcode(barcode)
    if item is None:
        return None
    return _food_item_to_response(item)


@router.post("/items", response_model=FoodItemResponse, status_code=201)
async def create_food_item(
    data: FoodItemCreate,
    current_user: User = Depends(get_current_user),
    food_svc: FoodItemService = Depends(get_food_item_service),
):
    item = food_svc.create(data, uid(current_user))
    return _food_item_to_response(item)


@router.get("/items/{item_id}", response_model=FoodItemResponse)
async def get_food_item(
    item_id: str,
    food_svc: FoodItemService = Depends(get_food_item_service),
):
    item = food_svc.get(item_id)
    return _food_item_to_response(item)


@router.get("/frequent", response_model=FoodItemSearchResponse)
async def get_frequent(
    current_user: User = Depends(get_current_user),
    food_svc: FoodItemService = Depends(get_food_item_service),
    limit: int = Query(20, ge=1, le=50),
):
    results = food_svc.get_frequent(uid(current_user), limit)
    return {"items": [_food_item_to_response(r) for r in results]}
