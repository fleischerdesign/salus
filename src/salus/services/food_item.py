from salus.exceptions import NotFoundError
from salus.models.food import FoodItem
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.food import FoodItemCreate


class FoodItemService:
    def __init__(self, uow: IUnitOfWork) -> None:
        self.uow = uow

    def search(self, query: str, limit: int = 20) -> list[FoodItem]:
        return self.uow.food_items.search(query, limit)

    def get(self, item_id: str) -> FoodItem:
        item = self.uow.food_items.get_by_id(item_id)
        if item is None:
            raise NotFoundError(f"FoodItem {item_id} not found")
        return item

    def find_by_barcode(self, barcode: str) -> FoodItem | None:
        return self.uow.food_items.find_by_barcode(barcode)

    def create(self, data: FoodItemCreate, user_id: str) -> FoodItem:
        item = FoodItem(
            user_id=user_id,
            name=data.name,
            brand=data.brand,
            barcode=data.barcode,
            serving_size=data.serving_size,
            serving_unit=data.serving_unit,
            calories_per_serving=data.calories_per_serving,
            protein_g=data.protein_g,
            carbs_g=data.carbs_g,
            fat_g=data.fat_g,
            fiber_g=data.fiber_g,
            sugar_g=data.sugar_g,
            saturated_fat_g=data.saturated_fat_g,
            sodium_mg=data.sodium_mg,
            source="manual",
        )
        return self.uow.food_items.create(item)

    def get_frequent(self, user_id: str, limit: int = 20) -> list[FoodItem]:
        return self.uow.food_items.find_frequent(user_id, limit)
