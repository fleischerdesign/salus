from __future__ import annotations

import json
from datetime import date
from typing import Any, TYPE_CHECKING

from salus.models.food import Meal, MealItem
from salus.models.measurement import Measurement
from salus.schemas.commands import CreateMealPayload, DeleteMealPayload, UpdateMealPayload
from salus.services._helpers import uid
from salus.services.command_registry import CommandResult, register
from salus.services.serialization import serialize_record
from salus.services.timezone import start_of_local_day, tz_for, user_today
from salus.utils import uuid7_str

if TYPE_CHECKING:
    from salus.repositories.unit_of_work import IUnitOfWork
    from salus.models.user import User

MEAL_SOURCE = "meal"
NUTRITION_METRIC = "nutrition"
NUTRITION_SOURCE = "nutrition"

_MEAL_FIELDS = (
    "id", "user_id", "log_date", "meal_type", "name", "notes",
    "created_at", "updated_at", "deleted_at",
)


def _calc_macros(items: list[MealItem], food_map: dict) -> dict:
    total = {"calories": 0.0, "protein_grams": 0.0, "carbs_grams": 0.0, "fat_grams": 0.0}
    for item in items:
        food = food_map.get(item.food_item_id)
        if food is None:
            continue
        factor = item.servings
        total["calories"] += food.calories_per_serving * factor
        total["protein_grams"] += food.protein_g * factor
        total["carbs_grams"] += food.carbs_g * factor
        total["fat_grams"] += food.fat_g * factor
    return total


def _resolve_food_items(uow: IUnitOfWork, items: list[MealItem]) -> dict:
    food_ids = {item.food_item_id for item in items}
    result: dict = {}
    for fid in food_ids:
        food = uow.food_items.get_by_id(fid)
        if food:
            result[fid] = food
    return result


def _measurement_for_meal(
    meal: Meal, items: list[MealItem], food_map: dict, tz, measurement_id: str | None
) -> Measurement:
    macros = _calc_macros(items, food_map)
    return Measurement(
        id=measurement_id,
        user_id=meal.user_id,
        metric_code=NUTRITION_METRIC,
        source_data_type=NUTRITION_SOURCE,
        source=MEAL_SOURCE,
        external_id=meal.id,
        value_json=json.dumps(macros),
        start_time=start_of_local_day(meal.log_date, tz),
    )


def _delete_measurement(uow: IUnitOfWork, meal_id: str) -> None:
    existing = uow.measurements.find_by_external_id(meal_id, MEAL_SOURCE)
    if existing:
        uow.measurements.delete(existing)


@register("create_meal")
class CreateMealHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = CreateMealPayload.model_validate(payload)
        user_id = uid(user)
        tz = tz_for(uow.session, user_id)
        if not data.items:
            return CommandResult(status="error", message="Meal must have at least one item")

        log_date = date.fromisoformat(data.log_date) if data.log_date else user_today(uow.session, user_id)
        meal = Meal(
            id=data.id or uuid7_str(),
            user_id=user_id,
            log_date=log_date,
            meal_type=data.meal_type,
            name=data.name,
            notes=data.notes,
        )
        uow.meals.add(meal)

        items = []
        for item_data in data.items:
            item = MealItem(
                id=item_data.id or uuid7_str(),
                meal_id=meal.id or "",
                user_id=user_id,
                food_item_id=item_data.food_item_id,
                servings=item_data.servings,
                amount_g=item_data.amount_g,
            )
            uow.meal_items.add(item)
            items.append(item)

        food_map = _resolve_food_items(uow, items)
        uow.measurements.add(_measurement_for_meal(meal, items, food_map, tz, data.measurement_id))

        uow.commit()
        uow.session.refresh(meal)
        return CommandResult(
            status="created",
            id=meal.id,
            record=serialize_record(meal, list(_MEAL_FIELDS)),
        )


@register("update_meal")
class UpdateMealHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = UpdateMealPayload.model_validate(payload)
        user_id = uid(user)
        meal = uow.meals.get_by_id(data.id)
        if not meal or meal.user_id != user_id:
            return CommandResult(status="not_found", message="Meal not found")

        if data.meal_type is not None:
            meal.meal_type = data.meal_type
        if data.name is not None:
            meal.name = data.name
        if data.notes is not None:
            meal.notes = data.notes
        uow.meals.add(meal)

        if data.items is not None:
            for old in uow.meal_items.find_by_meal(data.id):
                uow.meal_items.delete(old)

            items = []
            for item_data in data.items:
                item = MealItem(
                    id=item_data.id or uuid7_str(),
                    meal_id=data.id,
                    user_id=user_id,
                    food_item_id=item_data.food_item_id,
                    servings=item_data.servings,
                    amount_g=item_data.amount_g,
                )
                uow.meal_items.add(item)
                items.append(item)
        else:
            items = uow.meal_items.find_by_meal(data.id)

        _delete_measurement(uow, data.id)
        food_map = _resolve_food_items(uow, items)
        uow.measurements.add(
            _measurement_for_meal(meal, items, food_map, tz_for(uow.session, user_id), data.measurement_id)
        )

        uow.commit()
        uow.session.refresh(meal)
        return CommandResult(
            status="updated",
            id=meal.id,
            record=serialize_record(meal, list(_MEAL_FIELDS)),
        )


@register("delete_meal")
class DeleteMealHandler:
    def execute(self, uow: IUnitOfWork, user: User, payload: dict[str, Any]) -> CommandResult:
        data = DeleteMealPayload.model_validate(payload)
        meal = uow.meals.get_by_id(data.id)
        if not meal:
            return CommandResult(status="deleted", id=data.id)
        if meal.user_id != uid(user):
            return CommandResult(status="forbidden", message="Not your meal")

        for item in uow.meal_items.find_by_meal(data.id):
            uow.meal_items.delete(item)
        _delete_measurement(uow, data.id)
        uow.meals.delete(meal)
        uow.commit()
        return CommandResult(status="deleted", id=data.id)
