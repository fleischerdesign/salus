import io
import logging
from datetime import datetime, timezone
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Form, Request, HTTPException, Security, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select

from salus.dependencies import get_current_user, get_sharing_service, get_metric_type_service, get_leaderboard_service
from salus.models.user import User
from salus.models.sharing import ConnectionStatus, FederatedAccessLog, SharingRelationship
from salus.services._helpers import uid
from salus.services.sharing import SharingService
from salus.services.metric_type import MetricTypeService
from salus.services.leaderboard import LeaderboardService
from salus.exceptions import NotFoundError, ConflictError

logger = logging.getLogger("salus.routers.sharing")
router = APIRouter()
security = HTTPBearer(auto_error=False)


@router.get("/sharing", response_class=HTMLResponse)
async def sharing_base_redirect(request: Request):
    return RedirectResponse("/sharing/feed", status_code=303)


# ---------------------------------------------------------------------------
# Feed
# ---------------------------------------------------------------------------

@router.get("/sharing/feed", response_class=HTMLResponse)
async def sharing_feed_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    activities = sharing_svc.get_feed_activities(uid(current_user))
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/sharing_feed.html",
        {
            "current_user": current_user,
            "activities": activities,
        },
    )


# ---------------------------------------------------------------------------
# Leaderboard
# ---------------------------------------------------------------------------

@router.get("/sharing/leaderboard", response_class=HTMLResponse)
async def sharing_leaderboard_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
    error: Optional[str] = Query(None),
):
    user_id = uid(current_user)
    groups = leaderboard_svc.list_my_groups(user_id)

    group_infos = []
    for g in groups:
        try:
            assert g.id is not None
            rankings_data = leaderboard_svc.get_group_rankings(g.id, user_id)
            rankings = rankings_data["rankings"]
            my_rank = None
            my_score = 0.0
            for idx, r in enumerate(rankings):
                if r["is_me"]:
                    my_rank = idx + 1
                    my_score = r["score"]
                    break
        except Exception:
            my_rank = None
            my_score = 0.0
            rankings = []

        group_infos.append({
            "group": g,
            "rankings": rankings,
            "my_rank": my_rank,
            "my_score": my_score,
            "member_count": len(g.members),
        })

    return request.app.state.templates.TemplateResponse(
        request,
        "pages/sharing_leaderboard.html",
        {
            "current_user": current_user,
            "groups": group_infos,
            "error": error,
            "supported_metrics": [
                {"code": "steps", "name": "Steps", "icon": "footprint"},
                {"code": "workouts", "name": "Workouts Completed", "icon": "fitness_center"},
                {"code": "sleep", "name": "Sleep Duration", "icon": "bedtime"},
                {"code": "water", "name": "Water Intake", "icon": "local_drink"},
            ],
        },
    )


@router.post("/sharing/leaderboard/join")
async def sharing_leaderboard_join(
    request: Request,
    invite_code: str = Form(...),
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    user_id = uid(current_user)
    try:
        group = leaderboard_svc.join_by_code(user_id, invite_code.strip())
        assert group.id is not None
        return RedirectResponse(f"/sharing/leaderboard/{group.id}", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/sharing/leaderboard?error={str(e)}", status_code=303)


@router.post("/sharing/leaderboard/create")
async def sharing_leaderboard_create(
    request: Request,
    name: str = Form(...),
    metric_type_code: str = Form(...),
    time_frame: str = Form(...),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    user_id = uid(current_user)

    dt_start = None
    dt_end = None
    if time_frame == "custom":
        if start_date:
            try:
                dt_start = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                pass
        if end_date:
            try:
                dt_end = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                pass

    try:
        group = leaderboard_svc.create_group(
            creator_id=user_id,
            name=name,
            metric_type_code=metric_type_code,
            time_frame=time_frame,
            start_date=dt_start,
            end_date=dt_end,
        )
        assert group.id is not None
        return RedirectResponse(f"/sharing/leaderboard/{group.id}", status_code=303)
    except Exception as e:
        return RedirectResponse(f"/sharing/leaderboard?error={str(e)}", status_code=303)


@router.get("/sharing/leaderboard/{group_id}", response_class=HTMLResponse)
async def sharing_leaderboard_detail_page(
    group_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    user_id = uid(current_user)
    try:
        rankings_data = leaderboard_svc.get_group_rankings(group_id, user_id)
    except Exception as e:
        return RedirectResponse(f"/sharing/leaderboard?error={str(e)}", status_code=303)

    return request.app.state.templates.TemplateResponse(
        request,
        "pages/sharing_leaderboard_detail.html",
        {
            "current_user": current_user,
            "group": rankings_data["group"],
            "rankings": rankings_data["rankings"],
            "start_date": rankings_data["start_date"],
            "end_date": rankings_data["end_date"],
        },
    )


@router.post("/sharing/leaderboard/{group_id}/leave")
async def sharing_leaderboard_leave(
    group_id: int,
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    user_id = uid(current_user)
    try:
        leaderboard_svc.leave_group(user_id, group_id)
    except Exception as e:
        return RedirectResponse(f"/sharing/leaderboard?error={str(e)}", status_code=303)
    return RedirectResponse("/sharing/leaderboard", status_code=303)


@router.post("/sharing/leaderboard/{group_id}/delete")
async def sharing_leaderboard_delete(
    group_id: int,
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    user_id = uid(current_user)
    try:
        leaderboard_svc.delete_group(user_id, group_id)
    except Exception as e:
        return RedirectResponse(f"/sharing/leaderboard?error={str(e)}", status_code=303)
    return RedirectResponse("/sharing/leaderboard", status_code=303)


# ---------------------------------------------------------------------------
# Connections
# ---------------------------------------------------------------------------

def _build_connections_context(
    request: Request,
    current_user: User,
    sharing_svc: SharingService,
    metric_svc: MetricTypeService,
) -> dict:
    owner_id = uid(current_user)
    peers = sharing_svc.get_peer_connections(owner_id)
    pending_invitations = sharing_svc.get_pending_invitations(owner_id)
    metrics = metric_svc.find_all(owner_id)
    connect_url = (
        f"{request.base_url}sharing/connections?connect_to=@{current_user.username}"
    )
    return {
        "current_user": current_user,
        "peers": peers,
        "pending_invitations": pending_invitations,
        "metrics": metrics,
        "connect_url": connect_url,
        "connect_to_prefill": "",
        "error": None,
        "new_tokens": None,
    }


@router.get("/sharing/access-log", response_class=HTMLResponse)
async def sharing_access_log_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    with sharing_svc.uow:
        stmt = select(FederatedAccessLog).where(
            FederatedAccessLog.owner_id == uid(current_user)
        ).order_by(FederatedAccessLog.accessed_at.desc())  # type: ignore
        logs = sharing_svc.uow.session.exec(stmt).all()

    return request.app.state.templates.TemplateResponse(
        request,
        "pages/sharing_access_log.html",
        {"current_user": current_user, "logs": logs},
    )


@router.get("/sharing/connections", response_class=HTMLResponse)
async def sharing_connections_page(
    request: Request,
    connect_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    ctx = _build_connections_context(request, current_user, sharing_svc, metric_svc)
    ctx["connect_to_prefill"] = connect_to or ""
    return request.app.state.templates.TemplateResponse(
        request, "pages/sharing_connections.html", ctx
    )


@router.post("/sharing")
async def create_sharing(
    request: Request,
    grantee_handle: Annotated[str, Form()],
    metric_type_ids: Annotated[list[int], Form()] = [],
    expiration_days: Annotated[Optional[int], Form()] = None,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    owner_id = uid(current_user)
    if not metric_type_ids:
        ctx = _build_connections_context(request, current_user, sharing_svc, metric_svc)
        ctx["error"] = "Please select at least one metric type to share"
        return request.app.state.templates.TemplateResponse(
            request, "pages/sharing_connections.html", ctx
        )

    form_data = await request.form()
    errors: list[str] = []

    new_tokens = []
    for m_id in metric_type_ids:
        agg_level = str(form_data.get(f"aggregation_level_{m_id}", "daily_summary"))
        try:
            rel = sharing_svc.create_relationship(
                owner_id=owner_id,
                grantee_handle=grantee_handle,
                metric_type_id=m_id,
                aggregation_level=agg_level,
                expiration_days=expiration_days,
            )
            raw_token = getattr(rel, "raw_token", None)
            if raw_token:
                new_tokens.append({
                    "metric": rel.metric_type.name if rel.metric_type else f"Metric {m_id}",
                    "token": raw_token
                })
        except ConflictError:
            continue
        except NotFoundError as e:
            errors.append(str(e))

    if errors:
        ctx = _build_connections_context(request, current_user, sharing_svc, metric_svc)
        ctx["error"] = "; ".join(errors)
        return request.app.state.templates.TemplateResponse(
            request, "pages/sharing_connections.html", ctx
        )

    if new_tokens:
        ctx = _build_connections_context(request, current_user, sharing_svc, metric_svc)
        ctx["new_tokens"] = new_tokens
        ctx["grantee_handle"] = grantee_handle
        return request.app.state.templates.TemplateResponse(
            request, "pages/sharing_connections.html", ctx
        )

    return RedirectResponse("/sharing/connections", status_code=303)


@router.post("/sharing/{relationship_id}/accept")
async def accept_sharing(
    relationship_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    redirect_url = "/sharing/connections"
    try:
        sharing_svc.accept_relationship(uid(current_user), relationship_id)
    except (NotFoundError, ConflictError) as e:
        redirect_url = f"/sharing/connections?error={str(e)}"
    response = RedirectResponse(redirect_url, status_code=303)
    response.headers["HX-Redirect"] = redirect_url
    return response


@router.post("/sharing/{relationship_id}/decline")
async def decline_sharing(
    relationship_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    redirect_url = "/sharing/connections"
    try:
        sharing_svc.decline_relationship(uid(current_user), relationship_id)
    except (NotFoundError, ConflictError) as e:
        redirect_url = f"/sharing/connections?error={str(e)}"
    response = RedirectResponse(redirect_url, status_code=303)
    response.headers["HX-Redirect"] = redirect_url
    return response


@router.delete("/sharing/{relationship_id}", response_class=HTMLResponse)
async def delete_sharing(
    relationship_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    try:
        sharing_svc.deactivate_relationship(uid(current_user), relationship_id)
    except NotFoundError:
        pass
    response = HTMLResponse(content="")
    response.headers["HX-Refresh"] = "true"
    return response


@router.get("/sharing/connections/invite-modal", response_class=HTMLResponse)
async def invite_modal(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    connect_url = (
        f"{request.base_url}sharing/connections?connect_to=@{current_user.username}"
    )
    return request.app.state.templates.TemplateResponse(
        request,
        "components/sharing/invite_modal.html",
        {
            "connect_url": connect_url,
        },
    )


@router.get("/sharing/connections/invite-qr", response_class=StreamingResponse)
async def invite_qr(
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

@router.get("/api/v1/federation/sharing", response_class=JSONResponse)
async def federated_shared_data(
    request: Request,
    owner_username: Annotated[str, Query()],
    data_type: Annotated[str, Query()],
    date: Annotated[str, Query()],
    sharing_svc: SharingService = Depends(get_sharing_service),
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Security(security)] = None,
):
    sig_header = request.headers.get("Signature")
    sig_input_header = request.headers.get("Signature-Input")

    with sharing_svc.uow:
        owner = sharing_svc.uow.users.get_by_username(owner_username)
        if not owner:
            raise HTTPException(status_code=404, detail="Owner not found")

        metric_types = sharing_svc.uow.metric_types.find_all(owner.id)
        metric = next((m for m in metric_types if m.source_data_type == data_type), None)
        if not metric or metric.id is None:
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
                    body=None
                )
                stmt = select(SharingRelationship).where(
                    SharingRelationship.owner_id == owner.id,
                    SharingRelationship.grantee_handle == requester_handle,
                    SharingRelationship.metric_type_id == metric.id,
                    SharingRelationship.status == ConnectionStatus.ACTIVE,
                )
                rel = sharing_svc.uow.session.exec(stmt).first()
                if not rel:
                    raise HTTPException(status_code=401, detail="Unauthorized remote grantee")
            except Exception as exc:
                logger.warning(f"Signature authentication failed: {exc}")
                raise HTTPException(status_code=401, detail="Invalid cryptographic signature")
        else:
            if not credentials or not credentials.credentials:
                raise HTTPException(status_code=401, detail="Missing authorization credentials")
            token = credentials.credentials
            import hashlib
            token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

            ctx = select(SharingRelationship).where(
                SharingRelationship.api_token_hash == token_hash,
                SharingRelationship.owner_id == owner.id,
                SharingRelationship.metric_type_id == metric.id,
                SharingRelationship.status == ConnectionStatus.ACTIVE,
            )
            rel = sharing_svc.uow.session.exec(ctx).first()
            if not rel:
                raise HTTPException(status_code=401, detail="Invalid or inactive token")

        # Log this query in the GDPR audit log
        from salus.models.sharing import FederatedAccessLog
        access_log = FederatedAccessLog(
            owner_id=uid(owner),
            requester_handle=rel.grantee_handle,
            data_type=data_type,
            target_date=date,
        )
        sharing_svc.uow.session.add(access_log)

        raw_measurements = sharing_svc.uow.measurements.find_all(
            user_id=owner.id, data_types=[data_type]
        )

        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Expected YYYY-MM-DD."
            )

        day_measurements = [
            m for m in raw_measurements if m.start_time.date() == target_date
        ]

        if rel.aggregation_level == "daily_summary":
            if not day_measurements:
                return JSONResponse({"status": "ok", "data": []})
            values = [
                m.value_numeric for m in day_measurements if m.value_numeric is not None
            ]
            val = (
                sum(values)
                if data_type in ("steps", "water")
                else (sum(values) / len(values) if values else None)
            )
            result = [
                {
                    "data_type": data_type,
                    "value_numeric": val,
                    "start_time": date,
                    "source": "summary",
                    "external_id": f"summary-{owner_username}-{data_type}-{date}",
                }
            ]
        else:
            result = [
                {
                    "data_type": m.data_type,
                    "value_numeric": m.value_numeric,
                    "value_json": m.value_json,
                    "start_time": m.start_time.isoformat(),
                    "source": m.source,
                    "external_id": m.external_id,
                }
                for m in day_measurements
            ]

        return JSONResponse({"status": "ok", "data": result})


@router.post("/api/v1/federation/accept", response_class=JSONResponse)
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
        raise HTTPException(status_code=401, detail="Invalid token or relationship not found")
    except Exception:
        logger.exception("Unexpected error processing federation accept")
        raise HTTPException(status_code=500, detail="Internal server error")
    return JSONResponse({"status": "ok"})


@router.post("/api/v1/federation/notify-update", response_class=JSONResponse)
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
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token_hash = auth_header.split(" ", 1)[1]

    owner_handle = body.get("owner_handle")
    data_type = body.get("data_type")
    date_str = body.get("date")

    if not owner_handle or not data_type or not date_str:
        raise HTTPException(status_code=400, detail="Missing required fields: owner_handle, data_type, date")

    with sharing_svc.uow:
        stmt = select(SharingRelationship).where(
            SharingRelationship.api_token_hash == token_hash,
            SharingRelationship.status == ConnectionStatus.ACTIVE,
        )
        rel = sharing_svc.uow.session.exec(stmt).first()
        if not rel:
            raise HTTPException(status_code=401, detail="Unauthorized token hash")
        local_user_id = rel.owner_id

    import threading
    threading.Thread(
        target=sharing_svc.resolve_and_fetch,
        args=(local_user_id, owner_handle, data_type, date_str, True),
        daemon=True,
    ).start()

    return JSONResponse({"status": "ok", "message": "Update queued"})


@router.get("/.well-known/webfinger", response_class=JSONResponse)
async def webfinger_discover(
    resource: str,
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    if not resource.startswith("acct:"):
        raise HTTPException(status_code=400, detail="Invalid resource scheme. Expected acct:")

    parts = resource[5:].split("@", 1)
    username = parts[0]

    with sharing_svc.uow:
        user = sharing_svc.uow.users.get_by_username(username)
        if not user:
            raise HTTPException(status_code=404, detail="Actor not found")

    host = parts[1] if len(parts) > 1 else "localhost"
    scheme = "http" if "localhost" in host or "127.0.0.1" in host or "testserver" in host else "https"

    return JSONResponse({
        "subject": f"acct:{username}@{host}",
        "links": [
            {
                "rel": "self",
                "type": "application/activity+json",
                "href": f"{scheme}://{host}/api/v1/federation/actors/{username}"
            }
        ]
    })


@router.get("/api/v1/federation/actors/{username}", response_class=JSONResponse)
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

    return JSONResponse({
        "@context": [
            "https://www.w3.org/ns/activitystreams"
        ],
        "id": f"{base_url}/api/v1/federation/actors/{username}",
        "type": "Person",
        "preferredUsername": username,
        "endpoints": {
            "sharing": f"{base_url}/api/v1/federation/sharing",
            "accept": f"{base_url}/api/v1/federation/accept",
            "notify": f"{base_url}/api/v1/federation/notify-update"
        }
    })


@router.get("/api/v1/federation/access-log", response_class=JSONResponse)
async def federated_access_log(
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    from salus.models.sharing import FederatedAccessLog
    with sharing_svc.uow:
        stmt = select(FederatedAccessLog).where(
            FederatedAccessLog.owner_id == current_user.id
        ).order_by(FederatedAccessLog.accessed_at.desc())  # type: ignore
        logs = sharing_svc.uow.session.exec(stmt).all()

    return JSONResponse({
        "status": "ok",
        "logs": [
            {
                "id": log.id,
                "requester_handle": log.requester_handle,
                "data_type": log.data_type,
                "target_date": log.target_date,
                "accessed_at": log.accessed_at.isoformat(),
            }
            for log in logs
        ]
    })
