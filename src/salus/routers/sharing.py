from datetime import datetime, timezone, timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Form, Request, HTTPException, Security, Query
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import select

from salus.dependencies import get_current_user, get_sharing_service, get_metric_type_service, get_leaderboard_service
from salus.models.user import User
from salus.models.sharing import SharingRelationship
from salus.services._helpers import uid
from salus.services.sharing import SharingService
from salus.services.metric_type import MetricTypeService
from salus.services.leaderboard import LeaderboardService
from salus.exceptions import NotFoundError, ConflictError

router = APIRouter()
security = HTTPBearer()


@router.get("/sharing", response_class=HTMLResponse)
async def sharing_base_redirect(request: Request):
    return RedirectResponse("/sharing/feed", status_code=303)


@router.get("/sharing/feed", response_class=HTMLResponse)
async def sharing_feed_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    today = datetime.now(timezone.utc).date()
    activities = []
    
    # 1. Get incoming relationships (other users sharing with current user)
    with sharing_svc.uow:
        stmt = select(SharingRelationship).where(
            SharingRelationship.grantee_handle == f"@{current_user.username}",
            SharingRelationship.is_active
        )
        incoming = sharing_svc.uow.session.exec(stmt).all()
        
        friends_dict = {}
        for rel in incoming:
            if rel.owner_id not in friends_dict:
                friends_dict[rel.owner_id] = {
                    "user": rel.owner,
                    "metrics": []
                }
            friends_dict[rel.owner_id]["metrics"].append(rel.metric_type.source_data_type)

        # 2. Fetch achievements dynamically
        for friend_id, friend_data in friends_dict.items():
            friend_user = friend_data["user"]
            shared_types = friend_data["metrics"]
            
            # Fetch workouts completed in the last 3 days
            three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
            from salus.models.workout import WorkoutSession
            stmt_sessions = select(WorkoutSession).where(
                WorkoutSession.user_id == friend_id,
                WorkoutSession.completed_at.is_not(None),  # type: ignore
                WorkoutSession.completed_at >= three_days_ago  # type: ignore
            ).order_by(WorkoutSession.completed_at.desc())  # type: ignore
            sessions = sharing_svc.uow.session.exec(stmt_sessions).all()
            
            for sess in sessions:
                activities.append({
                    "type": "workout",
                    "friend_name": friend_user.username,
                    "time": sess.completed_at,
                    "title": sess.plan.name if sess.plan else "Workout Session",
                    "notes": sess.notes,
                    "id": f"workout-{sess.id}"
                })
                
            # Fetch step counts for today
            if "steps" in shared_types:
                raw_steps = sharing_svc.uow.measurements.find_all(user_id=friend_id, data_types=["steps"])
                today_steps = sum(m.value_numeric for m in raw_steps if m.start_time.date() == today and m.value_numeric is not None)
                if today_steps > 0:
                    activities.append({
                        "type": "steps",
                        "friend_name": friend_user.username,
                        "time": datetime.now(timezone.utc),
                        "value": int(today_steps),
                        "id": f"steps-{friend_id}-{today.isoformat()}"
                    })
                    
            # Fetch weight for today
            if "weight" in shared_types:
                raw_weight = sharing_svc.uow.measurements.find_all(user_id=friend_id, data_types=["weight"])
                today_weights = [m.value_numeric for m in raw_weight if m.start_time.date() == today and m.value_numeric is not None]
                if today_weights:
                    activities.append({
                        "type": "weight",
                        "friend_name": friend_user.username,
                        "time": datetime.now(timezone.utc),
                        "value": today_weights[-1],
                        "id": f"weight-{friend_id}-{today.isoformat()}"
                    })
    
    # Sort activities by time desc
    activities.sort(key=lambda x: x["time"] if isinstance(x["time"], datetime) else datetime.now(timezone.utc), reverse=True)
    
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/sharing_feed.html",
        {
            "current_user": current_user,
            "activities": activities,
        },
    )


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



@router.get("/sharing/connections", response_class=HTMLResponse)
async def sharing_connections_page(
    request: Request,
    connect_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    owner_id = uid(current_user)
    relationships = sharing_svc.list_relationships(owner_id)
    metrics = metric_svc.find_all(owner_id)
    
    # 1. Fetch incoming relationships
    with sharing_svc.uow:
        stmt = select(SharingRelationship).where(
            SharingRelationship.grantee_handle == f"@{current_user.username}",
            SharingRelationship.is_active
        )
        incoming_relationships = sharing_svc.uow.session.exec(stmt).all()
        
    # 2. Group outbound by handle
    outbound_groups = {}
    for rel in relationships:
        if not rel.is_active:
            continue
        handle = rel.grantee_handle
        if handle not in outbound_groups:
            outbound_groups[handle] = {
                "handle": handle,
                "metrics": [],
                "rel_ids": []
            }
        outbound_groups[handle]["metrics"].append(rel.metric_type.name)
        outbound_groups[handle]["rel_ids"].append(rel.id)

    # 3. Group inbound by owner
    inbound_groups = {}
    for rel in incoming_relationships:
        username = rel.owner.username
        handle = f"@{username}"
        if handle not in inbound_groups:
            inbound_groups[handle] = {
                "handle": handle,
                "metrics": [],
                "rel_ids": []
            }
        inbound_groups[handle]["metrics"].append(rel.metric_type.name)
        inbound_groups[handle]["rel_ids"].append(rel.id)
        
    connect_url = f"{request.base_url}sharing/connections?connect_to=@{current_user.username}"
    
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/sharing_connections.html",
        {
            "current_user": current_user,
            "outbound_groups": outbound_groups.values(),
            "inbound_groups": inbound_groups.values(),
            "metrics": metrics,
            "connect_to": connect_to,
            "connect_url": connect_url,
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
        # Load data to render the connections page with error
        relationships = sharing_svc.list_relationships(owner_id)
        metrics = metric_svc.find_all(owner_id)
        with sharing_svc.uow:
            stmt = select(SharingRelationship).where(
                SharingRelationship.grantee_handle == f"@{current_user.username}",
                SharingRelationship.is_active
            )
            incoming = sharing_svc.uow.session.exec(stmt).all()
        
        # Groupings
        outbound_groups = {}
        for rel in relationships:
            if not rel.is_active:
                continue
            handle = rel.grantee_handle
            if handle not in outbound_groups:
                outbound_groups[handle] = {"handle": handle, "metrics": [], "rel_ids": []}
            outbound_groups[handle]["metrics"].append(rel.metric_type.name)
            outbound_groups[handle]["rel_ids"].append(rel.id)

        inbound_groups = {}
        for rel in incoming:
            username = rel.owner.username
            handle = f"@{username}"
            if handle not in inbound_groups:
                inbound_groups[handle] = {"handle": handle, "metrics": [], "rel_ids": []}
            inbound_groups[handle]["metrics"].append(rel.metric_type.name)
            inbound_groups[handle]["rel_ids"].append(rel.id)
            
        connect_url = f"{request.base_url}sharing/connections?connect_to=@{current_user.username}"
        
        return request.app.state.templates.TemplateResponse(
            request,
            "pages/sharing_connections.html",
            {
                "current_user": current_user,
                "outbound_groups": outbound_groups.values(),
                "inbound_groups": inbound_groups.values(),
                "metrics": metrics,
                "error": "Please select at least one metric type to share",
                "connect_url": connect_url,
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
                continue
    except NotFoundError as e:
        relationships = sharing_svc.list_relationships(owner_id)
        metrics = metric_svc.find_all(owner_id)
        with sharing_svc.uow:
            stmt = select(SharingRelationship).where(
                SharingRelationship.grantee_handle == f"@{current_user.username}",
                SharingRelationship.is_active
            )
            incoming = sharing_svc.uow.session.exec(stmt).all()
        
        outbound_groups = {}
        for rel in relationships:
            if not rel.is_active:
                continue
            handle = rel.grantee_handle
            if handle not in outbound_groups:
                outbound_groups[handle] = {"handle": handle, "metrics": [], "rel_ids": []}
            outbound_groups[handle]["metrics"].append(rel.metric_type.name)
            outbound_groups[handle]["rel_ids"].append(rel.id)

        inbound_groups = {}
        for rel in incoming:
            username = rel.owner.username
            handle = f"@{username}"
            if handle not in inbound_groups:
                inbound_groups[handle] = {"handle": handle, "metrics": [], "rel_ids": []}
            inbound_groups[handle]["metrics"].append(rel.metric_type.name)
            inbound_groups[handle]["rel_ids"].append(rel.id)
            
        connect_url = f"{request.base_url}sharing/connections?connect_to=@{current_user.username}"
        
        return request.app.state.templates.TemplateResponse(
            request,
            "pages/sharing_connections.html",
            {
                "current_user": current_user,
                "outbound_groups": outbound_groups.values(),
                "inbound_groups": inbound_groups.values(),
                "metrics": metrics,
                "error": str(e),
                "connect_url": connect_url,
            },
        )
    
    return RedirectResponse("/sharing/connections", status_code=303)


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

        # Look up active sharing relationship matching the api_token_hash and not expired
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        stmt = select(SharingRelationship).where(
            SharingRelationship.owner_id == owner.id,
            SharingRelationship.metric_type_id == metric.id,
            SharingRelationship.api_token_hash == token,
            SharingRelationship.is_active,
            (SharingRelationship.expiration_date == None) | (SharingRelationship.expiration_date > now)  # type: ignore  # noqa: E711
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
