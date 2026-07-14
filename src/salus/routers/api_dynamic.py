from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import Response
from sqlmodel import Session, select

from salus.dependencies import get_current_user, get_unit_of_work
from salus.models.user import User
from salus.repositories.entity_meta import ENTITY_META, ENTITY_REGISTRY, EntityMeta
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.sync import SyncOperation
from salus.services.write_pipeline import WritePipeline

router = APIRouter(tags=["Entities"])

_STATUS_CODE_MAP = {"error": 400, "forbidden": 403, "not_found": 404, "conflict": 409}


def _get_meta(entity_name: str) -> EntityMeta:
    for e in ENTITY_META:
        if e.name == entity_name:
            return e
    raise HTTPException(status_code=500, detail=f"No entity meta for {entity_name}")


def _check_ownership(obj: object, user: User, meta: EntityMeta, session: Session) -> None:
    strategy = meta.strategy
    if strategy in ("user_scoped", "append_only"):
        owner_field = meta.owner_field or "user_id"
        if getattr(obj, owner_field) != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif strategy == "shared_nullable":
        owner_field = meta.owner_field or "user_id"
        obj_user = getattr(obj, owner_field, None)
        if obj_user is not None and obj_user != user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif strategy == "relational" and meta.parent_model and meta.parent_field and meta.parent_owner_field:
        fk = getattr(obj, meta.parent_field, None)
        if fk is not None:
            parent = session.get(meta.parent_model, fk)
            if parent and getattr(parent, meta.parent_owner_field) != user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
    # global: intentionally public-read (leaderboard groups/members)


def _build_list_query(model: type, meta: EntityMeta, user: User, page: int, limit: int):
    stmt = select(model)

    strategy = meta.strategy
    if strategy in ("user_scoped", "append_only"):
        owner_field = meta.owner_field or "user_id"
        stmt = stmt.where(getattr(model, owner_field) == user.id)
    elif strategy == "shared_nullable":
        owner_field = meta.owner_field or "user_id"
        col = getattr(model, owner_field)
        stmt = stmt.where((col == user.id) | (col.is_(None)))  # type: ignore[union-attr]
    elif (strategy == "relational"
          and meta.parent_model
          and meta.parent_field
          and meta.parent_owner_field):
        parent = meta.parent_model
        parent_pk = getattr(parent, "id")
        fk = getattr(model, meta.parent_field)
        stmt = stmt.join(parent, fk == parent_pk)  # type: ignore[arg-type]
        stmt = stmt.where(getattr(parent, meta.parent_owner_field) == user.id)

    if hasattr(model, "deleted_at"):
        stmt = stmt.where(getattr(model, "deleted_at").is_(None))  # type: ignore[union-attr]

    offset = (page - 1) * limit
    pk_col = getattr(model, "id")
    stmt = stmt.order_by(pk_col.desc()).offset(offset).limit(limit)  # type: ignore[union-attr]
    return stmt


def register_crud_routes(app: FastAPI) -> None:
    for entity_name in ENTITY_REGISTRY:
        _register_one(app, entity_name)


def _register_one(app: FastAPI, entity_name: str) -> None:
    model = ENTITY_REGISTRY[entity_name]
    meta = _get_meta(entity_name)

    async def create(
        request: Request,
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        body = await request.json()
        pipeline = WritePipeline(uow, user)
        op = SyncOperation(type="create", entity=entity_name, data=body)
        results = pipeline.process([op])
        result = results[0]
        if result.status in _STATUS_CODE_MAP:
            raise HTTPException(
                status_code=_STATUS_CODE_MAP.get(result.status, 400),
                detail=result.message or result.status,
            )
        return result.record or {"id": result.id, "status": result.status}

    async def update(
        id: str,
        request: Request,
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        body = await request.json()
        pipeline = WritePipeline(uow, user)
        op = SyncOperation(type="update", entity=entity_name, id=id, data=body)
        results = pipeline.process([op])
        result = results[0]
        if result.status in _STATUS_CODE_MAP:
            raise HTTPException(
                status_code=_STATUS_CODE_MAP.get(result.status, 400),
                detail=result.message or result.status,
            )
        return result.record or {"id": result.id, "status": result.status}

    async def delete(
        id: str,
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        pipeline = WritePipeline(uow, user)
        op = SyncOperation(type="delete", entity=entity_name, id=id)
        results = pipeline.process([op])
        result = results[0]
        if result.status in ("error", "forbidden", "not_found"):
            raise HTTPException(
                status_code=_STATUS_CODE_MAP.get(result.status, 400),
                detail=result.message or result.status,
            )
        return Response(status_code=204)

    async def get_one(
        id: str,
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        with uow:
            obj = uow.session.get(model, id)
            if obj is None:
                raise HTTPException(status_code=404, detail=f"{entity_name} not found")
            if hasattr(obj, "deleted_at") and obj.deleted_at is not None:  # pyright: ignore[reportAttributeAccessIssue]
                raise HTTPException(status_code=404, detail=f"{entity_name} not found")
            _check_ownership(obj, user, meta, uow.session)
            return obj.model_dump()  # type: ignore[union-attr]

    async def get_list(
        page: int = Query(1, ge=1),
        limit: int = Query(50, ge=1, le=200),
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        with uow:
            stmt = _build_list_query(model, meta, user, page, limit)
            results = list(uow.session.exec(stmt).all())
            return [r.model_dump() for r in results]  # type: ignore[union-attr]

    api_path = f"/api/v1/{entity_name}"
    app.add_api_route(api_path, create, methods=["POST"], name=f"create_{entity_name}")
    app.add_api_route(api_path, get_list, methods=["GET"], name=f"list_{entity_name}")
    app.add_api_route(f"{api_path}/{{id}}", update, methods=["PUT"], name=f"update_{entity_name}")
    app.add_api_route(f"{api_path}/{{id}}", delete, methods=["DELETE"], name=f"delete_{entity_name}")
    app.add_api_route(f"{api_path}/{{id}}", get_one, methods=["GET"], name=f"get_{entity_name}")
