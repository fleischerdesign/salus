from typing import Any

from fastapi import APIRouter, Depends, FastAPI, Request, Response
from sqlmodel import select

from salus.dependencies import get_current_user, get_unit_of_work
from salus.exceptions import ApiError, raise_from_command_result
from salus.models.user import User
from salus.repositories.entity_meta import ENTITY_META, EntityMeta, ENTITY_REGISTRY
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.sync import SyncOperation
from salus.services._helpers import uid
from salus.services.write_pipeline import WritePipeline

_PLURAL_MAP: dict[str, str] = {
    "metric_type": "metric-types",
    "measurement": "measurements",
    "goal": "goals",
    "circadian_profile": "circadian-profiles",
    "exercise": "exercises",
    "workout_plan": "workout-plans",
    "workout_plan_exercise": "workout-plan-exercises",
    "workout_session": "workout-sessions",
    "workout_log_entry": "workout-log-entries",
    "insight": "insights",
    "notification": "notifications",
    "dashboard_widget": "dashboard-widgets",
    "sharing_relationship": "sharing-relationships",
    "leaderboard_group": "leaderboard-groups",
    "leaderboard_member": "leaderboard-members",
    "share_recipient": "share-recipients",
    "asymmetric_share": "asymmetric-shares",
    "api_token": "api-tokens",
    "federated_access_log": "federated-access-logs",
    "user": "users",
}

_SKIP_AUTO_CRUD: set[str] = {
    "workout_plan_exercise",
    "workout_log_entry",
    "federated_access_log",
    "sync_push_log",
}


def register_auto_crud(app: FastAPI) -> None:
    for meta in ENTITY_META:
        if meta.name in _SKIP_AUTO_CRUD:
            continue
        plural = _PLURAL_MAP.get(meta.name, meta.name + "s")
        _register_entity_routes(app, meta, plural)


def _register_entity_routes(app: FastAPI, meta: EntityMeta, plural: str) -> None:
    router = APIRouter(prefix=f"/api/v1/{plural}", tags=[plural])

    @router.get("", response_model=list)
    async def list_all(
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        model_cls = ENTITY_REGISTRY[meta.name]
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
        if hasattr(model_cls, "deleted_at"):
            query = query.where(getattr(model_cls, "deleted_at").is_(None))
        rows = uow.session.exec(query).all()
        return [_serialize_row(r) for r in rows]

    @router.get("/{item_id}")
    async def get_one(
        item_id: str,
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        model_cls = ENTITY_REGISTRY[meta.name]
        obj = uow.session.get(model_cls, item_id)
        if not obj:
            raise ApiError(code="not_found", message="Resource not found", status_code=404)
        if hasattr(obj, "deleted_at") and getattr(obj, "deleted_at") is not None:
            raise ApiError(code="not_found", message="Resource not found", status_code=404)
        _check_ownership(obj, user, meta, uow.session)
        return _serialize_row(obj)

    @router.post("", status_code=201)
    async def create_one(
        request: Request,
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        body = await request.json()
        pipeline = WritePipeline(uow, user)
        op = SyncOperation(type="create", entity=meta.name, data=body)
        results = pipeline.process([op])
        result = results[0]
        raise_from_command_result(result.status, result.message)
        return result.record or {}

    @router.patch("/{item_id}")
    async def patch_one(
        item_id: str,
        request: Request,
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        body = await request.json()
        pipeline = WritePipeline(uow, user)
        op = SyncOperation(type="update", entity=meta.name, id=item_id, data=body)
        results = pipeline.process([op])
        result = results[0]
        raise_from_command_result(result.status, result.message)
        return result.record or {}

    @router.delete("/{item_id}", status_code=204)
    async def delete_one(
        item_id: str,
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        model_cls = ENTITY_REGISTRY[meta.name]
        obj = uow.session.get(model_cls, item_id)
        if not obj or (hasattr(obj, "deleted_at") and getattr(obj, "deleted_at") is not None):
            raise ApiError(code="not_found", message="Resource not found", status_code=404)
        _check_ownership(obj, user, meta, uow.session)

        pipeline = WritePipeline(uow, user)
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
            raise ApiError(code="forbidden", message="Not authorized", status_code=403)
    elif strategy == "shared_nullable":
        owner_field = meta.owner_field or "user_id"
        if hasattr(obj, owner_field):
            obj_user = getattr(obj, owner_field)
            if obj_user is not None and obj_user != uid_user:
                raise ApiError(code="forbidden", message="Not authorized", status_code=403)
    elif strategy == "global":
        pass


def _serialize_row(obj: Any) -> dict[str, Any]:
    from datetime import datetime

    if hasattr(obj, "model_dump"):
        result = obj.model_dump()
    elif hasattr(obj, "__dict__"):
        result = {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
    else:
        return {}
    for k, v in result.items():
        if isinstance(v, datetime):
            result[k] = v.replace(tzinfo=None).isoformat() if v.tzinfo else v.isoformat()
    return result
