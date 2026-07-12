from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request

from salus.dependencies import get_current_user, get_unit_of_work
from salus.models.user import User
from salus.repositories.entity_meta import ENTITY_REGISTRY
from salus.repositories.unit_of_work import IUnitOfWork
from salus.schemas.sync import SyncOperation
from salus.services.write_pipeline import WritePipeline

router = APIRouter(tags=["Entities"])


async def get_write_pipeline(
    uow: IUnitOfWork = Depends(get_unit_of_work),
    current_user: User = Depends(get_current_user),
) -> WritePipeline:
    return WritePipeline(uow, current_user)


def register_crud_routes(app: FastAPI) -> None:
    for entity_name, _entity_class in ENTITY_REGISTRY.items():
        _register_routes(app, entity_name)


def _register_routes(app: FastAPI, entity_name: str) -> None:
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
        if result.status in ("error", "forbidden", "not_found", "conflict"):
            status_map = {"error": 400, "forbidden": 403, "not_found": 404, "conflict": 409}
            raise HTTPException(status_code=status_map.get(result.status, 400), detail=result.message or result.status)
        return result.record or {"id": result.id, "status": result.status}

    async def update(
        id: int,
        request: Request,
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        body = await request.json()
        pipeline = WritePipeline(uow, user)
        op = SyncOperation(type="update", entity=entity_name, id=id, data=body)
        results = pipeline.process([op])
        result = results[0]
        if result.status in ("error", "forbidden", "not_found", "conflict"):
            status_map = {"error": 400, "forbidden": 403, "not_found": 404, "conflict": 409}
            raise HTTPException(status_code=status_map.get(result.status, 400), detail=result.message or result.status)
        return result.record or {"id": result.id, "status": result.status}

    async def delete(
        id: int,
        user: User = Depends(get_current_user),
        uow: IUnitOfWork = Depends(get_unit_of_work),
    ):
        pipeline = WritePipeline(uow, user)
        op = SyncOperation(type="delete", entity=entity_name, id=id)
        results = pipeline.process([op])
        result = results[0]
        if result.status in ("error", "forbidden", "not_found"):
            status_map = {"error": 400, "forbidden": 403, "not_found": 404}
            raise HTTPException(status_code=status_map.get(result.status, 400), detail=result.message or result.status)
        from fastapi.responses import Response
        return Response(status_code=204)

    api_path = f"/api/v1/{entity_name}"
    app.add_api_route(api_path, create, methods=["POST"], name=f"create_{entity_name}")
    app.add_api_route(f"{api_path}/{{id}}", update, methods=["PUT"], name=f"update_{entity_name}")
    app.add_api_route(f"{api_path}/{{id}}", delete, methods=["DELETE"], name=f"delete_{entity_name}")
