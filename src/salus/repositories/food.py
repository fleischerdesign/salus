from datetime import date

from sqlmodel import select

from salus.models.food import (
    FoodItem,
    Meal,
    MealItem,
    Recipe,
    RecipeIngredient,
)
from salus.repositories.base import Repository


class FoodItemRepository(Repository[FoodItem]):
    model = FoodItem

    def search(self, query: str, limit: int = 20) -> list[FoodItem]:
        return list(
            self.session.exec(
                select(FoodItem).where(
                    FoodItem.name.ilike(f"%{query}%"),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                    FoodItem.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).limit(limit)
            ).all()
        )

    def find_by_barcode(self, barcode: str) -> FoodItem | None:
        stmt = select(FoodItem).where(
            FoodItem.barcode == barcode,
            FoodItem.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        )
        return self.session.exec(stmt).first()

    def find_all_verified(self) -> list[FoodItem]:
        return list(
            self.session.exec(
                select(FoodItem).where(
                    FoodItem.is_verified == True,  # noqa: E712
                    FoodItem.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(FoodItem.name)  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_user(self, user_id: str) -> list[FoodItem]:
        return list(
            self.session.exec(
                select(FoodItem).where(
                    FoodItem.user_id == user_id,
                    FoodItem.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(FoodItem.name)  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_frequent(self, user_id: str, limit: int = 20) -> list[FoodItem]:
        return list(
            self.session.exec(
                select(FoodItem)
                .join(MealItem, MealItem.food_item_id == FoodItem.id)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                .where(
                    MealItem.user_id == user_id,
                    MealItem.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                    FoodItem.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
                .group_by(FoodItem.id)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                .order_by(FoodItem.id)  # pyright: ignore[reportAttributeAccessIssue]
                .limit(limit)
            ).all()
        )


class MealRepository(Repository[Meal]):
    model = Meal

    def find_by_user_and_date_range(self, user_id: str, since: date, until: date) -> list[Meal]:
        return list(
            self.session.exec(
                select(Meal).where(
                    Meal.user_id == user_id,
                    Meal.log_date >= since,
                    Meal.log_date <= until,
                    Meal.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(Meal.log_date.desc(), Meal.created_at.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_user_and_date(self, user_id: str, log_date: date) -> list[Meal]:
        return list(
            self.session.exec(
                select(Meal).where(
                    Meal.user_id == user_id,
                    Meal.log_date == log_date,
                    Meal.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(Meal.created_at.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )

    def find_by_user(self, user_id: str) -> list[Meal]:
        return list(
            self.session.exec(
                select(Meal).where(
                    Meal.user_id == user_id,
                    Meal.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(Meal.log_date.desc())  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )


class MealItemRepository(Repository[MealItem]):
    model = MealItem

    def find_by_meal(self, meal_id: str) -> list[MealItem]:
        return list(
            self.session.exec(
                select(MealItem).where(
                    MealItem.meal_id == meal_id,
                    MealItem.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
            ).all()
        )


class RecipeRepository(Repository[Recipe]):
    model = Recipe

    def find_by_user(self, user_id: str) -> list[Recipe]:
        return list(
            self.session.exec(
                select(Recipe).where(
                    Recipe.user_id == user_id,
                    Recipe.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                ).order_by(Recipe.name)  # pyright: ignore[reportAttributeAccessIssue]
            ).all()
        )


class RecipeIngredientRepository(Repository[RecipeIngredient]):
    model = RecipeIngredient

    def find_by_recipe(self, recipe_id: str) -> list[RecipeIngredient]:
        return list(
            self.session.exec(
                select(RecipeIngredient).where(
                    RecipeIngredient.recipe_id == recipe_id,
                    RecipeIngredient.deleted_at.is_(None),  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
                )
            ).all()
        )
