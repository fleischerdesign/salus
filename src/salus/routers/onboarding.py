from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from salus.database import get_session
from salus.dependencies import (
    get_api_token_service,
    get_current_user,
    get_goal_service,
    get_measurement_service,
    get_metric_type_service,
)
from salus.models.goal import GoalDirection, GoalFrequency
from salus.models.user import User
from salus.schemas.goal import GoalCreate
from salus.schemas.measurement import MeasurementCreate
from salus.services._helpers import uid
from salus.services.api_token import ApiTokenService
from salus.services.goal import GoalService
from salus.services.measurement import MeasurementService
from salus.services.metric_type import MetricTypeService

router = APIRouter()


@router.post("/onboarding/dismiss", response_class=HTMLResponse)
async def dismiss_onboarding(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    current_user.onboarding_dismissed = True
    session.add(current_user)
    session.commit()
    return HTMLResponse(status_code=200)


@router.post("/onboarding/token", response_class=HTMLResponse)
async def onboarding_create_token(
    request: Request,
    label: str = Form(),
    scopes: str = Form(default="ingest:write"),
    current_user: User = Depends(get_current_user),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    plaintext, _ = api_token_svc.create_token(uid(current_user), label, scopes)
    webhook_url = f"{request.base_url}webhook"
    return request.app.state.templates.TemplateResponse(
        request,
        "components/onboarding_token_result.html",
        {"plaintext_token": plaintext, "webhook_url": webhook_url},
    )


@router.post("/onboarding/entry", response_class=HTMLResponse)
async def onboarding_create_entry(
    request: Request,
    metric_type_id: int = Form(),
    value: str = Form(),
    current_user: User = Depends(get_current_user),
    measurement_service: MeasurementService = Depends(get_measurement_service),
):
    measurement_service.create(
        MeasurementCreate(value=value),
        metric_type_id,
        uid(current_user),
    )
    return request.app.state.templates.TemplateResponse(
        request,
        "components/onboarding_entry_result.html",
        {},
    )


@router.post("/onboarding/goal", response_class=HTMLResponse)
async def onboarding_create_goal(
    request: Request,
    metric_type_id: int = Form(),
    target_value: float = Form(),
    direction: str = Form(default="increase"),
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
):
    goal_service.create(
        GoalCreate(
            metric_type_id=metric_type_id,
            target_value=target_value,
            direction=GoalDirection(direction),
            frequency=GoalFrequency.DAILY,
        ),
        uid(current_user),
    )
    return request.app.state.templates.TemplateResponse(
        request,
        "components/onboarding_goal_result.html",
        {},
    )


_STEP_DEFS = [
    {
        "icon": "sync",
        "title": "Connect a Data Source",
        "description": "Generate an API token. Share the webhook URL with your wearables and apps to stream data into salus.",
        "template": "components/onboarding/step_token_body.html",
    },
    {
        "icon": "edit_note",
        "title": "Log Your First Entry",
        "description": "Manually track a metric — weight, mood, blood pressure, or whatever matters to you.",
        "template": "components/onboarding/step_entry_body.html",
    },
    {
        "icon": "track_changes",
        "title": "Set Your First Goal",
        "description": "Define a target — walk 10,000 steps per day, sleep 8 hours, or reach 80 kg.",
        "template": "components/onboarding/step_goal_body.html",
    },
]


@router.get("/onboarding/step/{n}/modal", response_class=HTMLResponse)
async def onboarding_step_modal(
    n: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    if n < 0 or n >= len(_STEP_DEFS):
        return HTMLResponse(status_code=404)

    step_def = _STEP_DEFS[n]
    metrics = metric_svc.find_all(uid(current_user))

    return request.app.state.templates.TemplateResponse(
        request,
        "components/onboarding/step_modal.html",
        {
            "step_index": n,
            "step_icon": step_def["icon"],
            "title": step_def["title"],
            "description": step_def["description"],
            "step_body_template": step_def["template"],
            "metrics": metrics,
        },
    )
