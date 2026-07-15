from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from salus.dependencies import (
    get_current_user,
    get_leaderboard_service,
    get_sharing_service,
)
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.leaderboard import LeaderboardService
from salus.services.sharing import SharingService

router = APIRouter(prefix="/api/v1")


class _CreateLeaderboardBody(BaseModel):
    name: str
    metric_type_code: str = "steps"
    time_frame: str = "weekly"


class _CreateConnectionBody(BaseModel):
    grantee_handle: str
    metric_type_id: str
    aggregation_level: str = "daily_summary"


class _JoinLeaderboardBody(BaseModel):
    invite_code: str


# ---------------------------------------------------------------------------
# Feed
# ---------------------------------------------------------------------------


@router.get("/sharing/feed")
async def api_sharing_feed(
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    return sharing_svc.get_feed_activities(uid(current_user))


# ---------------------------------------------------------------------------
# Leaderboard
# ---------------------------------------------------------------------------


@router.get("/sharing/leaderboard")
async def api_leaderboard_list(
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    groups = leaderboard_svc.list_my_groups(uid(current_user))
    return [
        {
            "id": g.id,
            "name": g.name,
            "creator_id": g.creator_id,
            "metric_type_code": g.metric_type_code,
            "time_frame": g.time_frame,
            "invite_code": g.invite_code,
            "start_date": g.start_date.isoformat() if g.start_date else None,
            "end_date": g.end_date.isoformat() if g.end_date else None,
            "created_at": g.created_at.isoformat() if g.created_at else None,
        }
        for g in groups
    ]


@router.post("/sharing/leaderboard", status_code=201)
async def api_leaderboard_create(
    body: _CreateLeaderboardBody,
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    group = leaderboard_svc.create_group(
        creator_id=uid(current_user),
        name=body.name,
        metric_type_code=body.metric_type_code,
        time_frame=body.time_frame,
    )
    return {
        "id": group.id,
        "name": group.name,
        "creator_id": group.creator_id,
        "metric_type_code": group.metric_type_code,
        "time_frame": group.time_frame,
        "invite_code": group.invite_code,
        "start_date": group.start_date.isoformat() if group.start_date else None,
        "end_date": group.end_date.isoformat() if group.end_date else None,
        "created_at": group.created_at.isoformat() if group.created_at else None,
    }


@router.get("/sharing/leaderboard/{group_id}")
async def api_leaderboard_get(
    group_id: str,
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    result = leaderboard_svc.get_group_rankings(group_id, uid(current_user))

    group = result["group"]
    rankings = result["rankings"]
    return {
        "group": {
            "id": group.id,
            "name": group.name,
            "creator_id": group.creator_id,
            "metric_type_code": group.metric_type_code,
            "time_frame": group.time_frame,
            "invite_code": group.invite_code,
            "start_date": group.start_date.isoformat() if group.start_date else None,
            "end_date": group.end_date.isoformat() if group.end_date else None,
            "created_at": group.created_at.isoformat() if group.created_at else None,
        },
        "rankings": rankings,
        "start_date": result["start_date"].isoformat(),
        "end_date": result["end_date"].isoformat(),
    }


@router.post("/sharing/leaderboard/{group_id}/join")
async def api_leaderboard_join(
    group_id: str,
    body: _JoinLeaderboardBody,
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    group = leaderboard_svc.join_by_code(uid(current_user), body.invite_code)

    return {
        "id": group.id,
        "name": group.name,
        "creator_id": group.creator_id,
        "metric_type_code": group.metric_type_code,
        "time_frame": group.time_frame,
        "invite_code": group.invite_code,
        "start_date": group.start_date.isoformat() if group.start_date else None,
        "end_date": group.end_date.isoformat() if group.end_date else None,
    }


@router.post("/sharing/leaderboard/{group_id}/leave", status_code=204)
async def api_leaderboard_leave(
    group_id: str,
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    leaderboard_svc.leave_group(uid(current_user), group_id)
    return Response(status_code=204)


@router.delete("/sharing/leaderboard/{group_id}", status_code=204)
async def api_leaderboard_delete(
    group_id: str,
    current_user: User = Depends(get_current_user),
    leaderboard_svc: LeaderboardService = Depends(get_leaderboard_service),
):
    leaderboard_svc.delete_group(uid(current_user), group_id)
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Connections
# ---------------------------------------------------------------------------


@router.get("/sharing/connections")
async def api_connections_list(
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    connections = sharing_svc.get_peer_connections(uid(current_user))
    return [
        {
            "handle": c.handle,
            "is_remote": c.is_remote,
            "is_pending": c.is_pending,
            "is_mutual": c.is_mutual,
            "expiration": c.expiration.isoformat() if c.expiration else None,
            "last_sync": c.last_sync,
            "metrics": [
                {
                    "metric_name": m.metric_name,
                    "icon": m.icon,
                    "color": m.color,
                    "aggregation": m.aggregation,
                    "direction": m.direction,
                    "relationship_id": m.relationship_id,
                }
                for m in c.metrics
            ],
        }
        for c in connections
    ]


@router.post("/sharing/connections", status_code=201)
async def api_connections_create(
    body: _CreateConnectionBody,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    rel = sharing_svc.create_relationship(
        owner_id=uid(current_user),
            grantee_handle=body.grantee_handle,
            metric_type_id=body.metric_type_id,
            aggregation_level=body.aggregation_level,
        )

    return {
        "id": rel.id,
        "owner_id": rel.owner_id,
        "grantee_handle": rel.grantee_handle,
        "metric_type_id": rel.metric_type_id,
        "aggregation_level": rel.aggregation_level,
        "status": rel.status,
        "created_at": rel.created_at.isoformat() if rel.created_at else None,
    }


@router.post("/sharing/connections/{connection_id}/accept", status_code=204)
async def api_connections_accept(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    sharing_svc.accept_relationship(uid(current_user), connection_id)
    return Response(status_code=204)


@router.post("/sharing/connections/{connection_id}/decline", status_code=204)
async def api_connections_decline(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    sharing_svc.decline_relationship(uid(current_user), connection_id)
    return Response(status_code=204)


@router.delete("/sharing/connections/{connection_id}", status_code=204)
async def api_connections_delete(
    connection_id: str,
    current_user: User = Depends(get_current_user),
    sharing_svc: SharingService = Depends(get_sharing_service),
):
    sharing_svc.deactivate_relationship(uid(current_user), connection_id)
    return Response(status_code=204)
