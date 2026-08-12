from typing import Any

from fastapi import APIRouter, Depends, FastAPI, Request, Response
from sqlmodel import select

from salus.dependencies import get_current_user_or_api, get_event_bus, get_unit_of_work
from salus.exceptions import ApiError, raise_from_command_result
from salus.models.user import User
from salus.repositories.entity_meta import (
    ENTITY_META,
    ENTITY_META_BY_NAME,
    ENTITY_REGISTRY,
    EntityMeta,
)
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.sync import SyncOperation
from salus.services._helpers import uid
from salus.services.entity_enrichment import ENRICHERS, RESPONSE_MODELS
from salus.services.event_bus import EventBus
from salus.services.write_pipeline import WritePipeline

_PLURAL_MAP: dict[str, str] = {
    "metric_group": "metric-groups",
    "metric_definition": "metric-definitions",
    "user_metric_preference": "user-metric-preferences",
    "user_source_preference": "user-source-preferences",
    "measurement": "measurements",
    "goal": "goals",
    "circadian_profile": "circadian-profiles",
    "exercise": "exercises",
    "workout_plan": "workout-plans",
    "workout_session": "workout-sessions",
    "insight": "insights",
    "notification": "notifications",
    "dashboard_widget": "dashboard-widgets",
    "sharing_relationship": "sharing-relationships",
    "leaderboard_group": "leaderboard-groups",
    "leaderboard_member": "leaderboard-members",
    "share_recipient": "share-recipients",
    "asymmetric_share": "asymmetric-shares",
    "habit": "habits",
    "mood_entry": "mood-entries",
    "mood_tag": "mood-tags",
    "journal_entry": "journal-entries",
    "medication": "medications",
    "food_item": "food-items",
}

# Entities whose CRUD is owned by a dedicated typed router, an auth/admin flow,
# or an internal pipeline — never by the generic CRUD generator.
_SKIP_AUTO_CRUD: set[str] = {
    # relational children with dedicated domain workflows
    "workout_plan_exercise",
    "workout_log_entry",
    # internal infrastructure tables
    "sync_push_log",
    "federated_access_log",
    # auth/credential resources, never a generic resource (password/token hashes)
    "user",
    "api_token",
    # dedicated typed routers own these domains (actions only; CRUD via auto-CRUD)
    "habit_log",
    "medication_schedule",
    "medication_log",
    "medication_inventory",
    # composed-aggregate domains: meal/recipe responses carry items/ingredients
    # and achievement exposes computed progress — not expressible as flat CRUD
    "meal",
    "meal_item",
    "recipe",
    "recipe_ingredient",
    "achievement_definition",
    "user_achievement",
}

# Write routes are only generated for entities whose data is user-owned.
# Global reference data (metric_definition, leaderboard_group, ...) and
# append-only records are immutable via the generic API — they mirror the
# sync strategy (EntityMeta.strategy) and stay read-only.
_WRITABLE_STRATEGIES: frozenset[str] = frozenset(
    {"user_scoped", "shared_nullable", "relational"}
)


def _validate_entity_map() -> None:
    unknown = [name for name in _PLURAL_MAP if name not in ENTITY_META_BY_NAME]
    if unknown:
        raise RuntimeError(f"auto-CRUD: unknown entities in _PLURAL_MAP: {unknown}")
    skipped_in_map = [name for name in _SKIP_AUTO_CRUD if name in _PLURAL_MAP]
    if skipped_in_map:
        raise RuntimeError(
            f"auto-CRUD: skipped entities must not be in _PLURAL_MAP: {skipped_in_map}"
        )
    unlisted = [
        meta.name
        for meta in ENTITY_META
        if meta.name not in _SKIP_AUTO_CRUD and meta.name not in _PLURAL_MAP
    ]
    if unlisted:
        raise RuntimeError(f"auto-CRUD: entities without a plural entry: {unlisted}")


def register_auto_crud(app: FastAPI) -> None:
    _validate_entity_map()
    for meta in ENTITY_META:
        if meta.name in _SKIP_AUTO_CRUD:
            continue
        _register_entity_routes(app, meta, _PLURAL_MAP[meta.name])


def _row_to_dict(obj: Any, extra: dict[str, Any] | None = None) -> dict[str, Any]:
    from datetime import date, datetime

    result = obj.model_dump() if hasattr(obj, "model_dump") else {}
    for k, v in result.items():
        if isinstance(v, datetime):
            result[k] = v.replace(tzinfo=None).isoformat()
        elif isinstance(v, date):
            result[k] = v.isoformat()
    if extra:
        result.update(extra)
    return result


def _register_entity_routes(app: FastAPI, meta: EntityMeta, plural: str) -> None:
    model_cls = ENTITY_REGISTRY[meta.name]
    response_model = RESPONSE_MODELS.get(meta.name, model_cls)
    router = APIRouter(prefix=f"/api/v1/{plural}", tags=[plural])

    @router.get("", response_model=list[response_model])
    async def list_all(
        request: Request,
        user: User = Depends(get_current_user_or_api),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        query = select(model_cls)
        strategy = meta.strategy
        uid_user = uid(user)
        owner_field = meta.owner_field or "user_id"
        if strategy == "user_scoped" and hasattr(model_cls, owner_field):
            query = query.where(getattr(model_cls, owner_field) == uid_user)
        elif strategy == "shared_nullable" and hasattr(model_cls, owner_field):
            query = query.where(
                (getattr(model_cls, owner_field) == uid_user)
                | (getattr(model_cls, owner_field).is_(None))
            )
        for key, value in request.query_params.items():
            if hasattr(model_cls, key) and value != "":
                query = query.where(getattr(model_cls, key) == value)
        if hasattr(model_cls, "deleted_at"):
            query = query.where(getattr(model_cls, "deleted_at").is_(None))
        rows = list(uow.session.exec(query).all())
        if meta.name in RESPONSE_MODELS:
            enriched = (
                ENRICHERS[meta.name](uow, uid_user, rows)
                if meta.name in ENRICHERS
                else {}
            )
            return [_row_to_dict(r, enriched.get(getattr(r, "id", "") or "", {})) for r in rows]
        return rows

    @router.get("/{item_id}", response_model=response_model)
    async def get_one(
        item_id: str,
        user: User = Depends(get_current_user_or_api),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        obj = uow.session.get(model_cls, item_id)
        if not obj:
            raise ApiError(code="not_found", message="Resource not found", status_code=404)
        if hasattr(obj, "deleted_at") and getattr(obj, "deleted_at") is not None:
            raise ApiError(code="not_found", message="Resource not found", status_code=404)
        _check_ownership(obj, user, meta, uow.session)
        if meta.name in RESPONSE_MODELS:
            enriched = (
                ENRICHERS[meta.name](uow, uid(user), [obj])
                if meta.name in ENRICHERS
                else {}
            )
            return _row_to_dict(obj, enriched.get(getattr(obj, "id", "") or "", {}))
        return obj

    if meta.strategy in _WRITABLE_STRATEGIES:
        @router.post("", status_code=201, response_model=response_model)
        async def create_one(
            request: Request,
            user: User = Depends(get_current_user_or_api),
            uow: IUnitOfWork = Depends(get_unit_of_work),
            event_bus: EventBus = Depends(get_event_bus),
        ):
            body = await request.json()
            pipeline = WritePipeline(uow, user, event_bus)
            op = SyncOperation(type="create", entity=meta.name, data=body)
            results = pipeline.process([op])
            result = results[0]
            raise_from_command_result(result.status, result.message)
            return result.record or {}

        @router.put("/{item_id}", response_model=response_model)
        @router.patch("/{item_id}", response_model=response_model)
        async def patch_one(
            item_id: str,
            request: Request,
            user: User = Depends(get_current_user_or_api),
            uow: IUnitOfWork = Depends(get_unit_of_work),
            event_bus: EventBus = Depends(get_event_bus),
        ):
            body = await request.json()
            pipeline = WritePipeline(uow, user, event_bus)
            op = SyncOperation(type="update", entity=meta.name, id=item_id, data=body)
            results = pipeline.process([op])
            result = results[0]
            raise_from_command_result(result.status, result.message)
            return result.record or {}

        @router.delete("/{item_id}", status_code=204)
        async def delete_one(
            item_id: str,
            user: User = Depends(get_current_user_or_api),
            uow: IUnitOfWork = Depends(get_unit_of_work),
            event_bus: EventBus = Depends(get_event_bus),
        ):
            obj = uow.session.get(model_cls, item_id)
            if not obj or (hasattr(obj, "deleted_at") and getattr(obj, "deleted_at") is not None):
                raise ApiError(code="not_found", message="Resource not found", status_code=404)
            _check_ownership(obj, user, meta, uow.session)

            pipeline = WritePipeline(uow, user, event_bus)
            op = SyncOperation(type="delete", entity=meta.name, id=item_id)
            results = pipeline.process([op])
            result = results[0]
            raise_from_command_result(result.status, result.message)
            return Response(status_code=204)

    app.include_router(router)


def _check_ownership(obj: Any, user: User, meta: EntityMeta, session: Any) -> None:
    uid_user = uid(user)
    strategy = meta.strategy
    if strategy == "user_scoped":
        owner_field = meta.owner_field or "user_id"
        if hasattr(obj, owner_field) and getattr(obj, owner_field) != uid_user:
            raise ApiError(code="not_found", message="Resource not found", status_code=404)
    elif strategy == "shared_nullable":
        owner_field = meta.owner_field or "user_id"
        if hasattr(obj, owner_field):
            obj_user = getattr(obj, owner_field)
            if obj_user is not None and obj_user != uid_user:
                raise ApiError(code="not_found", message="Resource not found", status_code=404)
    elif strategy == "global":
        pass
