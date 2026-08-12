import hashlib
import io
import logging

from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Security
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from salus.dependencies import (
    get_current_user,
    get_sharing_service,
    limiter,
)
from salus.models.user import User
from salus.services.sharing import SharingService
from salus.services.sharing._tasks import run_background
from salus.exceptions import NotFoundError
from salus.services._helpers import uid

logger = logging.getLogger("salus.routers.sharing")
router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/sharing/connections/invite-qr")
@limiter.limit("10/minute")
async def invite_qr(
    request: Request,
    url: str = Query(...),
):
    import qrcode

    img = qrcode.make(url, border=2)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


# ---------------------------------------------------------------------------
# Federation API
# ---------------------------------------------------------------------------


@router.get("/api/v1/federation/sharing")
async def federated_shared_data(
    request: Request,
    owner_username: Annotated[str, Query()],
    source_data_type: Annotated[str, Query()],
    date: Annotated[str, Query()],
    end_date: Annotated[Optional[str], Query()] = None,
    sharing_svc: SharingService = Depends(get_sharing_service),
    credentials: Annotated[
        Optional[HTTPAuthorizationCredentials], Security(security)
    ] = None,
):
    sig_header = request.headers.get("Signature")
    sig_input_header = request.headers.get("Signature-Input")

    with sharing_svc.uow:
        owner = sharing_svc.uow.users.get_by_username(owner_username)
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")

        metric_defs = sharing_svc.uow.metric_definitions.find_all()
        metric = next(
            (m for m in metric_defs if m.source_data_type == source_data_type), None
        )
        if not metric:
            return JSONResponse({"status": "ok", "data": []})

        if sig_header and sig_input_header:
            path_with_query = request.url.path
            if request.url.query:
                path_with_query = f"{path_with_query}?{request.url.query}"
            try:
                requester_handle = sharing_svc.verify_request_signature(
                    headers_dict=dict(request.headers),
                    method=request.method,
                    path_with_query=path_with_query,
                    authority=request.url.netloc,
                    body=None,
                )
                rel = sharing_svc.uow.sharing_relationships.find_active_with_owner_metric_and_grantee(
                    uid(owner), requester_handle, metric.code
                )
                if not rel:
                    raise HTTPException(
                        status_code=401, detail="Unauthorized remote grantee"
                    )
            except Exception as exc:
                logger.warning(f"Signature authentication failed: {exc}")
                raise HTTPException(
                    status_code=401, detail="Invalid cryptographic signature"
                )
        else:
            if not credentials or not credentials.credentials:
                raise HTTPException(
                    status_code=401, detail="Missing authorization credentials"
                )
            token = credentials.credentials
            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

            rel = sharing_svc.uow.sharing_relationships.find_active_by_token_hash(
                token_hash
            )
            if not rel or rel.owner_id != owner.id or rel.metric_code != metric.code:
                raise HTTPException(status_code=401, detail="Invalid or inactive token")

        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Expected YYYY-MM-DD."
            )

        if end_date:
            try:
                parsed_end = datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid end_date format. Expected YYYY-MM-DD.",
                )
            result = sharing_svc.serve_shared_range(
                owner_username=owner_username,
                owner_id=uid(owner),
                requester_handle=rel.grantee_handle,
                source_data_type=source_data_type,
                start_date=target_date,
                end_date=parsed_end,
                aggregation_level=rel.aggregation_level,
            )
        else:
            result = sharing_svc.serve_shared_day(
                owner_username=owner_username,
                owner_id=uid(owner),
                requester_handle=rel.grantee_handle,
                source_data_type=source_data_type,
                date_str=date,
                target_date=target_date,
                aggregation_level=rel.aggregation_level,
            )

        return JSONResponse({"status": "ok", "data": result})


@router.post("/api/v1/federation/accept")
@limiter.limit("10/minute")
async def federated_accept(
    request: Request,
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    token = body.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Missing token")

    try:
        sharing_svc.process_federation_accept(token, body.get("owner_handle", ""))
    except NotFoundError as e:
        logger.warning(f"Federation accept failed: {e}")
        raise HTTPException(
            status_code=401, detail="Invalid token or relationship not found"
        )
    except Exception:
        logger.exception("Unexpected error processing federation accept")
        raise HTTPException(status_code=500, detail="Internal server error")
    return JSONResponse({"status": "ok"})


@router.post("/api/v1/federation/notify-update")
@limiter.limit("10/minute")
async def federated_notify_update(
    request: Request,
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid Authorization header"
        )
    token_hash = auth_header.split(" ", 1)[1]

    owner_handle = body.get("owner_handle")
    source_data_type = body.get("source_data_type")
    date_str = body.get("date")

    if not owner_handle or not source_data_type or not date_str:
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: owner_handle, source_data_type, date",
        )

    with sharing_svc.uow:
        rel = sharing_svc.uow.sharing_relationships.find_active_by_token_hash(
            token_hash
        )
        if not rel:
            raise HTTPException(status_code=401, detail="Unauthorized token hash")
        local_user_id = rel.owner_id

    run_background(
        sharing_svc.resolve_and_fetch,
        local_user_id,
        owner_handle,
        source_data_type,
        date_str,
        True,
        name="federation-refresh",
    )

    return JSONResponse({"status": "ok", "message": "Update queued"})


@router.get("/.well-known/webfinger")
@limiter.limit("10/minute")
async def webfinger_discover(
    request: Request,
    resource: str,
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    if not resource.startswith("acct:"):
        raise HTTPException(
            status_code=400, detail="Invalid resource scheme. Expected acct:"
        )

    parts = resource[5:].split("@", 1)
    username = parts[0]

    with sharing_svc.uow:
        user = sharing_svc.uow.users.get_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="Actor not found")

    host = parts[1] if len(parts) > 1 else "localhost"
    scheme = (
        "http"
        if "localhost" in host or "127.0.0.1" in host or "testserver" in host
        else "https"
    )

    return JSONResponse(
        {
            "subject": f"acct:{username}@{host}",
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"{scheme}://{host}/api/v1/federation/actors/{username}",
                }
            ],
        }
    )


@router.get("/api/v1/federation/actors/{username}")
@limiter.limit("10/minute")
async def federated_actor_profile(
    username: str,
    request: Request,
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    with sharing_svc.uow:
        user = sharing_svc.uow.users.get_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="Actor profile not found")

    base_url = str(request.base_url)
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    return JSONResponse(
        {
            "@context": ["https://www.w3.org/ns/activitystreams"],
            "id": f"{base_url}/api/v1/federation/actors/{username}",
            "type": "Person",
            "preferredUsername": username,
            "endpoints": {
                "sharing": f"{base_url}/api/v1/federation/sharing",
                "accept": f"{base_url}/api/v1/federation/accept",
                "notify": f"{base_url}/api/v1/federation/notify-update",
            },
        }
    )


@router.get("/api/v1/federation/access-log")
async def federated_access_log(
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    with sharing_svc.uow:
        logs = sharing_svc.uow.federated_access_logs.find_by_owner(uid(current_user))

    return JSONResponse(
        {
            "status": "ok",
            "logs": [
                {
                    "id": log.id,
                    "requester_handle": log.requester_handle,
                    "source_data_type": log.source_data_type,
                    "target_date": log.target_date,
                    "accessed_at": log.accessed_at.isoformat(),
                }
                for log in logs
            ],
        }
    )
