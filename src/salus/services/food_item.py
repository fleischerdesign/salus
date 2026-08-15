import httpx

from sqlmodel import select

from salus.exceptions import NotFoundError
from salus.models.food import FoodItem
from salus.repositories.protocols import ISystemConfigRepository
from salus.repositories.system_config import SystemConfigRepository
from salus.repositories.unit_of_work import IUnitOfWork
from salus.services.config import ConfigService
from salus.services.constants import SOURCE_OPENFOODFACTS, SOURCE_SYSTEM
from salus.services.food_reference import COMMON_FOODS
from salus.utils import uuid7_str

_OFF_API = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
_OFF_USER_AGENT = "SalusHealth/0.1 (self-hosted health tracker)"


def _lookup_openfoodfacts(barcode: str) -> dict | None:
    """Look up a barcode on OpenFoodFacts and map it to food_item fields (per 100 g)."""
    try:
        resp = httpx.get(
            _OFF_API.format(barcode=barcode),
            headers={"User-Agent": _OFF_USER_AGENT},
            timeout=10.0,
        )
        if resp.status_code != 200:
            return None
        payload = resp.json()
        if payload.get("status") != 1:
            return None
        product = payload.get("product") or {}
        name = (
            product.get("product_name")
            or product.get("product_name_en")
            or f"Produkt {barcode}"
        )
        nutriments = product.get("nutriments") or {}
        return {
            "name": name,
            "brand": product.get("brands"),
            "calories_per_serving": nutriments.get("energy-kcal_100g"),
            "protein_g": nutriments.get("proteins_100g"),
            "carbs_g": nutriments.get("carbohydrates_100g"),
            "fat_g": nutriments.get("fat_100g"),
            "fiber_g": nutriments.get("fiber_100g"),
            "sugar_g": nutriments.get("sugars_100g"),
            "saturated_fat_g": nutriments.get("saturated-fat_100g"),
            "sodium_mg": nutriments.get("sodium_100g"),
        }
    except Exception:
        return None


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
        existing = self.uow.food_items.find_by_barcode(barcode)
        if existing:
            return existing
        if not self._off_enabled():
            return None
        data = _lookup_openfoodfacts(barcode)
        if data is None:
            return None
        item = FoodItem(
            id=uuid7_str(),
            name=data["name"],
            brand=data.get("brand"),
            barcode=barcode,
            serving_size=100,
            serving_unit="g",
            calories_per_serving=data.get("calories_per_serving") or 0,
            protein_g=data.get("protein_g") or 0,
            carbs_g=data.get("carbs_g") or 0,
            fat_g=data.get("fat_g") or 0,
            fiber_g=data.get("fiber_g"),
            sugar_g=data.get("sugar_g"),
            saturated_fat_g=data.get("saturated_fat_g"),
            sodium_mg=data.get("sodium_mg"),
            is_verified=True,
            user_id=None,
            source=SOURCE_OPENFOODFACTS,
        )
        self.uow.food_items.add(item)
        self.uow.commit()
        return item

    def get_frequent(self, user_id: str, limit: int = 20) -> list[FoodItem]:
        return self.uow.food_items.find_frequent(user_id, limit)

    def import_items(self, items: list[dict]) -> int:
        """Bulk-import curated foods as verified system items (idempotent by barcode/name)."""
        session = self.uow.session
        existing_barcodes = {
            item.barcode for item in session.exec(select(FoodItem)).all() if item.barcode
        }
        existing_names = {
            item.name for item in session.exec(select(FoodItem)).all() if item.name
        }
        count = 0
        for raw in items:
            name = (raw.get("name") or "").strip()
            barcode = raw.get("barcode") or None
            if not name:
                continue
            if barcode and barcode in existing_barcodes:
                continue
            if not barcode and name in existing_names:
                continue
            session.add(FoodItem(
                id=uuid7_str(),
                name=name,
                brand=raw.get("brand"),
                barcode=barcode,
                serving_size=raw.get("serving_size", 100),
                serving_unit=raw.get("serving_unit", "g"),
                calories_per_serving=raw.get("calories_per_serving") or 0,
                protein_g=raw.get("protein_g") or 0,
                carbs_g=raw.get("carbs_g") or 0,
                fat_g=raw.get("fat_g") or 0,
                fiber_g=raw.get("fiber_g"),
                sugar_g=raw.get("sugar_g"),
                saturated_fat_g=raw.get("saturated_fat_g"),
                sodium_mg=raw.get("sodium_mg"),
                is_verified=True,
                user_id=None,
                source=raw.get("source") or SOURCE_SYSTEM,
            ))
            if barcode:
                existing_barcodes.add(barcode)
            existing_names.add(name)
            count += 1
        return count

    def seed_common_foods(self) -> int:
        session = self.uow.session
        count = 0
        for data in COMMON_FOODS:
            if session.get(FoodItem, data["id"]) is None:
                session.add(FoodItem(
                    id=data["id"],
                    name=data["name"],
                    serving_size=data.get("serving_size", 100),
                    serving_unit="g",
                    calories_per_serving=data.get("calories_per_serving", 0),
                    protein_g=data.get("protein_g", 0),
                    carbs_g=data.get("carbs_g", 0),
                    fat_g=data.get("fat_g", 0),
                    fiber_g=data.get("fiber_g"),
                    sugar_g=data.get("sugar_g"),
                    saturated_fat_g=data.get("saturated_fat_g"),
                    sodium_mg=data.get("sodium_mg"),
                    is_verified=True,
                    user_id=None,
                    source=SOURCE_SYSTEM,
                ))
                count += 1
        return count

    def _off_enabled(self) -> bool:
        cfg: ISystemConfigRepository = SystemConfigRepository(self.uow.session)
        value = ConfigService(cfg).get_resolved_value("food_off_enabled")
        if value == "":
            return True
        return value.strip().lower() in ("1", "true", "yes", "on")
