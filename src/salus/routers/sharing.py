from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Form, Request, HTTPException, Security, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select

from salus.dependencies import get_current_user, get_sharing_service, get_metric_type_service
from salus.models.user import User
from salus.models.sharing import SharingRelationship
from salus.services._helpers import uid
from salus.services.sharing import SharingService
from salus.services.metric_type import MetricTypeService
from salus.exceptions import NotFoundError, ConflictError

router = APIRouter()
security = HTTPBearer()


@router.get("/sharing", response_class=HTMLResponse)
async def list_sharing(
    request: Request,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    owner_id = uid(current_user)
    relationships = sharing_svc.list_relationships(owner_id)
    metrics = metric_svc.find_all(owner_id)
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/sharing.html",
        {
            "current_user": current_user,
            "relationships": relationships,
            "metrics": metrics,
        },
    )


@router.post("/sharing")
async def create_sharing(
    request: Request,
    grantee_handle: Annotated[str, Form()],
    metric_type_ids: list[int] = Form(default=[]),
    expiration_days: Annotated[Optional[int], Form()] = None,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    owner_id = uid(current_user)
    if not metric_type_ids:
        relationships = sharing_svc.list_relationships(owner_id)
        metrics = metric_svc.find_all(owner_id)
        return request.app.state.templates.TemplateResponse(
            request,
            "pages/sharing.html",
            {
                "current_user": current_user,
                "relationships": relationships,
                "metrics": metrics,
                "error": "Please select at least one metric type to share",
            },
        )

    form_data = await request.form()

    try:
        for m_id in metric_type_ids:
            agg_level = str(form_data.get(f"aggregation_level_{m_id}", "daily_summary"))
            try:
                sharing_svc.create_relationship(
                    owner_id=owner_id,
                    grantee_handle=grantee_handle,
                    metric_type_id=m_id,
                    aggregation_level=agg_level,
                    expiration_days=expiration_days,
                )
            except ConflictError:
                # If one is already shared, skip it to be user friendly
                continue
    except NotFoundError as e:
        relationships = sharing_svc.list_relationships(owner_id)
        metrics = metric_svc.find_all(owner_id)
        return request.app.state.templates.TemplateResponse(
            request,
            "pages/sharing.html",
            {
                "current_user": current_user,
                "relationships": relationships,
                "metrics": metrics,
                "error": str(e),
            },
        )
    
    # Redirect back to sharing index to show new relationships list
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/sharing", status_code=303)


@router.delete("/sharing/{relationship_id}", response_class=HTMLResponse)
async def delete_sharing(
    relationship_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    owner_id = uid(current_user)
    try:
        sharing_svc.deactivate_relationship(owner_id, relationship_id)
    except NotFoundError:
        pass
    relationships = sharing_svc.list_relationships(owner_id)
    return request.app.state.templates.TemplateResponse(
        request,
        "components/sharing/relationship_list.html",
        {"relationships": relationships},
    )


# --------------------------------------------------------------------------
# Federation Endpoint: Shared Data Fetch (Token Authorized)
# --------------------------------------------------------------------------

@router.get("/api/v1/federation/sharing", response_class=JSONResponse)
async def federated_shared_data(
    owner_username: str = Query(...),
    data_type: str = Query(...),
    date: str = Query(...),
    credentials: HTTPAuthorizationCredentials = Security(security),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    token = credentials.credentials
    # Fetch from unit of work
    uow = sharing_svc.uow
    with uow:
        # Resolve owner user
        owner = uow.users.get_by_username(owner_username)
        if not owner:
            raise HTTPException(status_code=404, detail="Owner user not found")

        # Resolve metric type
        metric_types = uow.metric_types.find_all(owner.id)
        metric = next((m for m in metric_types if m.source_data_type == data_type), None)
        if not metric:
            raise HTTPException(status_code=404, detail="Metric type not found")

        # Look up active sharing relationship matching the api_token_hash
        stmt = select(SharingRelationship).where(
            SharingRelationship.owner_id == owner.id,
            SharingRelationship.metric_type_id == metric.id,
            SharingRelationship.api_token_hash == token,
            SharingRelationship.is_active
        )
        from salus.repositories.unit_of_work import SqlUnitOfWork
        relationship = None
        if isinstance(uow, SqlUnitOfWork):
            relationship = uow.session.exec(stmt).first()
        
    if not relationship:
        raise HTTPException(status_code=401, detail="Unauthorized: invalid or inactive sharing token")

    # Access verified: Fetch & return data
    # Resolve and aggregate using SharingService
    try:
        # Since resolve_and_fetch expects a requester_id, we can map requester_id
        # based on the relationship grantee_handle. If grantee is local, get their user.
        # But wait! For API calls, requester_id is just used to obtain the requester's username
        # to cross-validate relationship.get_active_relationship.
        # Let's write a simple query directly to avoid needing requester_id for remote requests.
        with uow:
            raw_measurements = uow.measurements.find_all(
                user_id=owner.id,
                data_types=[data_type]
            )
            from datetime import datetime
            try:
                target_date = datetime.strptime(date, "%Y-%m-%d").date()
            except ValueError:
                target_date = datetime.utcnow().date()

            day_measurements = [
                m for m in raw_measurements 
                if m.start_time.date() == target_date
            ]

            if relationship.aggregation_level == "daily_summary":
                if not day_measurements:
                    results = []
                else:
                    values = [m.value_numeric for m in day_measurements if m.value_numeric is not None]
                    val = sum(values) if data_type in ("steps", "water") else (sum(values)/len(values) if values else None)
                    results = [{
                        "data_type": data_type,
                        "value_numeric": val,
                        "start_time": date,
                        "source": "summary",
                        "external_id": f"summary-{owner_username}-{data_type}-{date}"
                    }]
            else:
                results = [
                    {
                        "data_type": m.data_type,
                        "value_numeric": m.value_numeric,
                        "value_json": m.value_json,
                        "start_time": m.start_time.isoformat(),
                        "source": m.source,
                        "external_id": m.external_id
                    }
                    for m in day_measurements
                ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok", "data": results}
