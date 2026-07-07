from datetime import date

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from salus.dependencies import (
    get_current_user,
    get_goal_service,
    get_metric_type_service,
)
from salus.models.goal import GoalDirection, GoalFrequency
from salus.models.user import User
from salus.schemas.goal import GoalCreate
from salus.services._helpers import uid
from salus.services.goal import GoalService
from salus.services.metric_type import MetricTypeService

router = APIRouter()


def _render_goals_page(
    request: Request,
    user_id: int,
    current_user: User,
    goal_service: GoalService,
    metric_service: MetricTypeService,
) -> HTMLResponse:
    goals = goal_service.find_all(user_id)
    metrics = {m.id: m for m in metric_service.find_all(user_id)}
    goal_cards = []
    for g in goals:
        progress = goal_service.progress(g)
        metric = metrics.get(g.metric_type_id)
        goal_cards.append(
            {
                "goal": g,
                "progress": progress,
                "metric_name": metric.name if metric else "?",
                "metric_unit": metric.unit if metric else "",
            }
        )

    return request.app.state.templates.TemplateResponse(
        request,
        "pages/goals.html",
        {
            "current_user": current_user,
            "goal_cards": goal_cards,
            "all_metrics": [
                {"id": m.id, "name": m.name, "unit": m.unit} for m in metrics.values()
            ],
        },
    )


@router.get("", response_class=HTMLResponse)
async def list_goals(
    request: Request,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    return _render_goals_page(
        request, uid(current_user), current_user, goal_service, metric_service
    )


@router.get("/new", response_class=HTMLResponse)
async def new_goal_form(
    request: Request,
    current_user: User = Depends(get_current_user),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    user_id = uid(current_user)
    metrics = metric_service.find_all(user_id)
    return request.app.state.templates.TemplateResponse(
        request,
        "components/goal_form.html",
        {
            "goal": None,
            "all_metrics": [
                {"id": m.id, "name": m.name, "unit": m.unit} for m in metrics
            ],
        },
    )


@router.post("", response_class=HTMLResponse)
async def create_goal(
    request: Request,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
    metric_type_id: int = Form(...),
    target_value: float = Form(...),
    direction: str = Form("increase"),
    frequency: str = Form("daily"),
    deadline: str | None = Form(None),
):
    user_id = uid(current_user)
    deadline_date = date.fromisoformat(deadline) if deadline else None
    data = GoalCreate(
        metric_type_id=metric_type_id,
        target_value=target_value,
        direction=GoalDirection(direction),
        frequency=GoalFrequency(frequency),
        deadline=deadline_date,
    )
    goal_service.create(data, user_id)
    return RedirectResponse(url="/goals", status_code=303)


@router.delete("/{goal_id}", response_class=HTMLResponse)
async def delete_goal(
    request: Request,
    goal_id: int,
    current_user: User = Depends(get_current_user),
    goal_service: GoalService = Depends(get_goal_service),
    metric_service: MetricTypeService = Depends(get_metric_type_service),
):
    user_id = uid(current_user)
    goal_service.delete(goal_id, user_id)
    return _render_goals_page(
        request, user_id, current_user, goal_service, metric_service
    )
