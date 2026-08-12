"""Computed read enrichment for auto-CRUD.

Entities with derived fields (e.g. habit stats) register an enricher and a
response model here. auto-CRUD applies the enricher to fetched rows and
validates the result against the response model, so the generic generator
can serve read models that carry computed fields without a hand-written
per-entity router.

An enricher maps ``{row_id: {extra_field: value}}``; auto-CRUD merges those
fields into the serialized row before response-model validation.
"""
from typing import Any, Callable

from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.food import FoodItemResponse
from salus.schemas.habit import HabitResponse
from salus.schemas.journal import JournalEntryResponse
from salus.schemas.medication import MedicationResponse
from salus.services.habit import HabitService

Enricher = Callable[[IUnitOfWork, str, list[Any]], dict[str, dict[str, Any]]]

ENRICHERS: dict[str, Enricher] = {}
RESPONSE_MODELS: dict[str, type] = {}


def register_enricher(entity: str) -> Callable[[Enricher], Enricher]:
    def decorator(fn: Enricher) -> Enricher:
        ENRICHERS[entity] = fn
        return fn

    return decorator


def register_response_model(entity: str, model: type) -> None:
    RESPONSE_MODELS[entity] = model


@register_enricher("habit")
def _habit_enricher(
    uow: IUnitOfWork, user_id: str, rows: list[Any]
) -> dict[str, dict[str, Any]]:
    return HabitService(uow).get_all_habits_stats(user_id)


register_response_model("habit", HabitResponse)
register_response_model("journal_entry", JournalEntryResponse)
register_response_model("medication", MedicationResponse)
register_response_model("food_item", FoodItemResponse)
