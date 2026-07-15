
from fastapi import APIRouter, Depends, Query, Request, Response
from pydantic import BaseModel

from salus.dependencies import (
    get_api_token_service,
    get_circadian_service,
    get_current_user,
    get_goal_service,
    get_insight_service,
    get_measurement_service,
    get_notification_service,
    get_user_service,
)
from salus.models.goal import GoalDirection, GoalFrequency
from salus.models.user import User
from salus.schemas.analytics import InsightResponse
from salus.schemas.circadian import CircadianProfileCreate
from salus.schemas.goal import GoalCreate
from salus.schemas.measurement import MeasurementCreate
from salus.services._helpers import uid
from salus.services.api_token import ApiTokenService
from salus.services.circadian import CircadianService
from salus.services.goal import GoalService
from salus.services.insight.service import InsightService
from salus.services.measurement import MeasurementService
from salus.services.notification import NotificationService
from salus.services.user import UserService

router = APIRouter(prefix="/api/v1")


class _OnboardingEntryBody(BaseModel):
    metric_type_id: str
    value: str
    notes: str | None = None


class _OnboardingGoalBody(BaseModel):
    metric_type_id: str
    target_value: float
    direction: str = "increase"


class GoalCreateResponse(BaseModel):
    id: str
    metric_type_id: str
    target_value: float
    direction: str
    frequency: str
    deadline: str | None = None


class _CircadianProfileResponse(BaseModel):
    id: str
    user_id: str
    latitude: float | None = None
    longitude: float | None = None
    timezone_offset_hours: int | None = None
    configured_chronotype: str | None = None


class _OnboardingTokenResponse(BaseModel):
    token: str
    webhook_url: str


class _OnboardingEntryResponse(BaseModel):
    id: str
    metric_type_id: str
    value: str | float | None = None
    timestamp: str | None = None


# ── Goals ──

@router.get("/goals", response_model=list[GoalCreateResponse])
async def api_list_goals(
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
):
    goals = goal_service.find_all(uid(current_user))
    return [
        {
            "id": g.id,
            "metric_type_id": g.metric_type_id,
            "target_value": g.target_value,
            "direction": g.direction.value,
            "frequency": g.frequency.value,
            "deadline": g.deadline.isoformat() if g.deadline else None,
        }
        for g in goals
    ]


@router.post("/goals", response_model=GoalCreateResponse, status_code=201)
async def api_create_goal(
    data: GoalCreate,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
):
    goal = goal_service.create(data, uid(current_user))
    return {
        "id": goal.id,
        "metric_type_id": goal.metric_type_id,
        "target_value": goal.target_value,
        "direction": goal.direction.value,
        "frequency": goal.frequency.value,
        "deadline": goal.deadline.isoformat() if goal.deadline else None,
    }


@router.delete("/goals/{goal_id}", status_code=204)
async def api_delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
):
    goal_service.delete(goal_id, uid(current_user))
    return Response(status_code=204)


# ── Insights ──

@router.post("/insights/generate", response_model=InsightResponse, status_code=201)
async def api_generate_insight(
    date: str = Query(...),
    current_user: User = Depends(get_current_user),
    service: InsightService = Depends(get_insight_service),
):
    insight = service.generate_daily_insight(uid(current_user), date)
    return {
        "id": insight.id,
        "date": insight.query_date,
        "content": insight.content,
        "model_used": insight.model_used,
    }


# ── Circadian ──

@router.post("/circadian/profile", response_model=_CircadianProfileResponse)
async def api_circadian_profile(
    data: CircadianProfileCreate,
    current_user: User = Depends(get_current_user),
    service: CircadianService = Depends(get_circadian_service),
):
    profile = service.save_profile(user_id=uid(current_user), data=data)
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "latitude": profile.latitude,
        "longitude": profile.longitude,
        "timezone_offset_hours": profile.timezone_offset_hours,
        "configured_chronotype": profile.configured_chronotype,
    }


# ── Notifications ──

@router.post("/notifications/{notification_id}/read", status_code=204)
async def api_mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    service.mark_as_read(uid(current_user), notification_id)
    return Response(status_code=204)


@router.post("/notifications/read-all", status_code=204)
async def api_mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    service.mark_all_as_read(uid(current_user))
    return Response(status_code=204)


# ── Onboarding ──

@router.post("/onboarding/dismiss", status_code=204)
async def api_dismiss_onboarding(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    user_service.dismiss_onboarding(uid(current_user))
    return Response(status_code=204)


@router.post("/onboarding/token", response_model=_OnboardingTokenResponse)
async def api_onboarding_token(
    request: Request,
    label: str = Query("Webhook Token"),
    scopes: str = Query("ingest:write"),
    current_user: User = Depends(get_current_user),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    plaintext, _ = api_token_svc.create_token(uid(current_user), label, scopes)
    webhook_url = f"{request.base_url}webhook"
    return {"token": plaintext, "webhook_url": webhook_url}


@router.post("/onboarding/entry", response_model=_OnboardingEntryResponse, status_code=201)
async def api_onboarding_entry(
    body: _OnboardingEntryBody,
    current_user: User = Depends(get_current_user),
    measurement_service: MeasurementService = Depends(get_measurement_service),
):
    entry = measurement_service.create(
        MeasurementCreate(value=body.value, notes=body.notes),
        body.metric_type_id,
        uid(current_user),
    )
    return {
        "id": entry.id,
        "metric_type_id": entry.metric_type_id,
        "value": entry.display_value,
        "timestamp": entry.start_time.isoformat() if entry.start_time else None,
    }


@router.post("/onboarding/goal", response_model=GoalCreateResponse, status_code=201)
async def api_onboarding_goal(
    body: _OnboardingGoalBody,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
):
    data = GoalCreate(
        metric_type_id=body.metric_type_id,
        target_value=body.target_value,
        direction=GoalDirection(body.direction),
        frequency=GoalFrequency.DAILY,
    )
    goal = goal_service.create(data, uid(current_user))
    return {
        "id": goal.id,
        "metric_type_id": goal.metric_type_id,
        "target_value": goal.target_value,
        "direction": goal.direction.value,
        "frequency": goal.frequency.value,
        "deadline": goal.deadline.isoformat() if goal.deadline else None,
    }
