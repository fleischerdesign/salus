import json
from datetime import date, datetime, timezone

from salus.exceptions import ApiError, NotFoundError
from salus.models.food import Meal, MealItem
from salus.models.measurement import Measurement
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.food import MealCreate, MealUpdate


def _calc_macros(items, food_items_by_id: dict) -> dict:
    total = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    for item in items:
        food = food_items_by_id.get(item.food_item_id)
        if food is None:
            continue
        factor = item.servings
        total["calories"] += food.calories_per_serving * factor
        total["protein_g"] += food.protein_g * factor
        total["carbs_g"] += food.carbs_g * factor
        total["fat_g"] += food.fat_g * factor
    return total


def _items_to_response(items, food_items_by_id: dict) -> list[dict]:
    result = []
    for item in items:
        food = food_items_by_id.get(item.food_item_id)
        name = food.name if food else ""
        result.append({
            "id": item.id,
            "food_item_id": item.food_item_id,
            "food_item_name": name,
            "servings": item.servings,
            "amount_g": item.amount_g,
            "calories": food.calories_per_serving * item.servings if food else 0.0,
            "protein_g": food.protein_g * item.servings if food else 0.0,
            "carbs_g": food.carbs_g * item.servings if food else 0.0,
            "fat_g": food.fat_g * item.servings if food else 0.0,
        })
    return result


class MealService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def _get(self, meal_id: str, user_id: str) -> Meal:
        m = self.uow.meals.get_by_id(meal_id)
        if m is None or m.user_id != user_id:
            raise NotFoundError(f"Meal {meal_id} not found")
        return m

    def _resolve_food_items(self, meal_items: list[MealItem]) -> dict:
        food_ids = {item.food_item_id for item in meal_items}
        result = {}
        for fid in food_ids:
            food = self.uow.food_items.get_by_id(fid)
            if food:
                result[fid] = food
        return result

    def _measurement_for_meal(self, meal: Meal, items: list[MealItem], food_map: dict) -> Measurement:
        macros = _calc_macros(items, food_map)
        return Measurement(
            user_id=meal.user_id,
            metric_code="nutrition",
            data_type="nutrition",
            source="meal",
            external_id=meal.id,
            value_json=json.dumps(macros),
            start_time=datetime(
                meal.log_date.year, meal.log_date.month, meal.log_date.day,
                0, 0, 0, tzinfo=timezone.utc,
            ),
        )

    def _delete_measurement_for_meal(self, meal: Meal) -> None:
        existing = self.uow.measurements.find_by_external_id(meal.id, "meal")
        if existing:
            self.uow.measurements.delete(existing)

    def _meal_to_response(self, meal: Meal, items: list[MealItem], food_map: dict) -> dict:
        macros = _calc_macros(items, food_map)
        return {
            "id": meal.id,
            "log_date": meal.log_date.isoformat(),
            "meal_type": meal.meal_type,
            "name": meal.name,
            "notes": meal.notes,
            "items": _items_to_response(items, food_map),
            "total_calories": round(macros["calories"], 1),
            "total_protein_g": round(macros["protein_g"], 1),
            "total_carbs_g": round(macros["carbs_g"], 1),
            "total_fat_g": round(macros["fat_g"], 1),
            "created_at": meal.created_at.isoformat() if meal.created_at else "",
        }

    # ── CRUD ──

    def find_by_date(
        self, user_id: str, since: date | None = None, until: date | None = None
    ) -> list[dict]:
        if since is None:
            since = date.today()
        if until is None:
            until = date.today()
        meals = self.uow.meals.find_by_user_and_date_range(user_id, since, until)
        result = []
        for meal in meals:
            items = self.uow.meal_items.find_by_meal(meal.id or "")
            food_map = self._resolve_food_items(items)
            result.append(self._meal_to_response(meal, items, food_map))
        return result

    def get(self, meal_id: str, user_id: str) -> dict:
        meal = self._get(meal_id, user_id)
        items = self.uow.meal_items.find_by_meal(meal_id)
        food_map = self._resolve_food_items(items)
        return self._meal_to_response(meal, items, food_map)

    def create(self, data: MealCreate, user_id: str) -> dict:
        if not data.items:
            raise ApiError(code="empty_meal", message="Meal must have at least one item", status_code=400)

        log_date = date.fromisoformat(data.log_date) if data.log_date else date.today()
        meal = Meal(
            user_id=user_id,
            log_date=log_date,
            meal_type=data.meal_type,
            name=data.name,
            notes=data.notes,
        )
        self.uow.meals.create(meal)

        items = []
        for item_data in data.items:
            item = MealItem(
                meal_id=meal.id or "",
                user_id=user_id,
                food_item_id=item_data.food_item_id,
                servings=item_data.servings,
                amount_g=item_data.amount_g,
            )
            self.uow.meal_items.create(item)
            items.append(item)

        food_map = self._resolve_food_items(items)
        measurement = self._measurement_for_meal(meal, items, food_map)
        self.uow.measurements.create(measurement)

        return self._meal_to_response(meal, items, food_map)

    def update(self, meal_id: str, user_id: str, data: MealUpdate) -> dict:
        meal = self._get(meal_id, user_id)

        if data.meal_type is not None:
            meal.meal_type = data.meal_type
        if data.name is not None:
            meal.name = data.name
        if data.notes is not None:
            meal.notes = data.notes
        self.uow.meals.update(meal)

        if data.items is not None:
            old_items = self.uow.meal_items.find_by_meal(meal_id)
            for item in old_items:
                self.uow.meal_items.delete(item)

            items = []
            for item_data in data.items:
                item = MealItem(
                    meal_id=meal.id or "",
                    user_id=user_id,
                    food_item_id=item_data.food_item_id,
                    servings=item_data.servings,
                    amount_g=item_data.amount_g,
                )
                self.uow.meal_items.create(item)
                items.append(item)
        else:
            items = self.uow.meal_items.find_by_meal(meal_id)

        self._delete_measurement_for_meal(meal)
        food_map = self._resolve_food_items(items)
        measurement = self._measurement_for_meal(meal, items, food_map)
        self.uow.measurements.create(measurement)

        return self._meal_to_response(meal, items, food_map)

    def delete(self, meal_id: str, user_id: str) -> None:
        meal = self._get(meal_id, user_id)
        items = self.uow.meal_items.find_by_meal(meal_id)
        for item in items:
            self.uow.meal_items.delete(item)
        self._delete_measurement_for_meal(meal)
        self.uow.meals.delete(meal)

    # ── Today + Summary ──

    def get_today(self, user_id: str) -> list[dict]:
        meals = self.uow.meals.find_by_user_and_date(user_id, date.today())
        result = []
        for meal in meals:
            items = self.uow.meal_items.find_by_meal(meal.id or "")
            food_map = self._resolve_food_items(items)
            result.append(self._meal_to_response(meal, items, food_map))
        return result

    def get_summary(
        self, user_id: str, since: date | None = None, until: date | None = None
    ) -> list[dict]:
        if since is None:
            since = date.today()
        if until is None:
            until = date.today()

        meals = self.uow.meals.find_by_user_and_date_range(user_id, since, until)
        by_date: dict[str, dict] = {}
        for meal in meals:
            d = meal.log_date.isoformat()
            if d not in by_date:
                by_date[d] = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "count": 0}
            items = self.uow.meal_items.find_by_meal(meal.id or "")
            food_map = self._resolve_food_items(items)
            macros = _calc_macros(items, food_map)
            by_date[d]["calories"] += macros["calories"]
            by_date[d]["protein_g"] += macros["protein_g"]
            by_date[d]["carbs_g"] += macros["carbs_g"]
            by_date[d]["fat_g"] += macros["fat_g"]
            by_date[d]["count"] += 1

        return sorted(
            [
                {
                    "date": d,
                    "total_calories": round(v["calories"], 1),
                    "total_protein_g": round(v["protein_g"], 1),
                    "total_carbs_g": round(v["carbs_g"], 1),
                    "total_fat_g": round(v["fat_g"], 1),
                    "meal_count": v["count"],
                }
                for d, v in by_date.items()
            ],
            key=lambda x: x["date"],
            reverse=True,
        )
