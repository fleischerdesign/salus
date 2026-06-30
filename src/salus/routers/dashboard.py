from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, Response

from salus.dependencies import (
    get_current_user,
    get_dashboard_widget_service,
    get_metric_type_service,
)
from salus.models.dashboard import WidgetSize
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.dashboard_widget import DashboardWidgetService
from salus.services.metric_type import MetricTypeService

router = APIRouter()


def _date_nav_context(target_date: str) -> dict:
    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
    today_str = datetime.today().strftime("%Y-%m-%d")
    prev_dt = target_dt - timedelta(days=1)
    next_dt = target_dt + timedelta(days=1)
    is_today = target_date == today_str
    can_go_next = target_dt.date() < datetime.today().date()
    return {
        "display_date": target_date,
        "display_date_formatted": target_dt.strftime("%a, %b %d, %Y"),
        "prev_date": prev_dt.strftime("%Y-%m-%d"),
        "next_date": next_dt.strftime("%Y-%m-%d"),
        "is_today": is_today,
        "can_go_next": can_go_next,
    }


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    date: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    user_id = uid(current_user)
    today_str = datetime.today().strftime("%Y-%m-%d")
    target_date = date if date else today_str
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        target_date = today_str

    widgets = widget_svc.ensure_defaults(user_id)
    widget_contexts = [widget_svc.widget_data(w, user_id=user_id, date=target_date) for w in widgets]
    metrics = metric_svc.find_all(user_id)

    nav = _date_nav_context(target_date)

    return request.app.state.templates.TemplateResponse(
        request,
        "pages/dashboard.html",
        {
            "current_user": current_user,
            "widget_contexts": widget_contexts,
            "show_onboarding": not current_user.onboarding_dismissed,
            "metrics": metrics,
            **nav,
        },
    )


@router.get("/dashboard/grid", response_class=HTMLResponse)
async def dashboard_grid(
    request: Request,
    date: str | None = Query(None),
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    user_id = uid(current_user)
    today_str = datetime.today().strftime("%Y-%m-%d")
    target_date = date if date else today_str
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        target_date = today_str

    widgets = widget_svc.ensure_defaults(user_id)
    widget_contexts = [widget_svc.widget_data(w, user_id=user_id, date=target_date) for w in widgets]
    nav = _date_nav_context(target_date)

    return request.app.state.templates.TemplateResponse(
        request,
        "components/dashboard/day_navigator_block.html",
        {"widget_contexts": widget_contexts, **nav},
    )


@router.get("/dashboard/widgets/add-modal", response_class=HTMLResponse)
async def add_widget_modal(
    request: Request,
    current_user: User = Depends(get_current_user),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    metrics = metric_svc.find_all(uid(current_user))
    return request.app.state.templates.TemplateResponse(
        request,
        "components/dashboard/add_widget_modal.html",
        {"metrics": metrics},
    )


@router.post("/dashboard/widgets/add", response_class=HTMLResponse)
async def add_widget(
    request: Request,
    metric_type_id: int = Form(),
    size: str = Form(),
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget = widget_svc.add_widget(uid(current_user), metric_type_id, WidgetSize(size))
    ctx = widget_svc.widget_data(widget, user_id=uid(current_user))
    html = request.app.state.templates.get_template(
        "components/dashboard/widget_chrome.html"
    ).render({**ctx})
    return HTMLResponse(
        content=html,
        headers={"HX-Trigger": "widgetAdded"},
    )


@router.get("/dashboard/widgets/{widget_id}", response_class=HTMLResponse)
async def get_widget(
    widget_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget = widget_svc.get_widget(widget_id, uid(current_user))
    ctx = widget_svc.widget_data(widget, user_id=uid(current_user))
    return request.app.state.templates.TemplateResponse(
        request,
        "components/dashboard/widget_chrome.html",
        ctx,
    )


@router.post("/dashboard/widgets/reorder")
async def reorder_widgets(
    ids: str = Form(),
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    ordered = [int(i) for i in ids.split(",") if i.strip().isdigit()]
    widget_svc.reorder(uid(current_user), ordered)
    return Response(status_code=204)


@router.get("/dashboard/widgets/{widget_id}/edit", response_class=HTMLResponse)
async def edit_widget_modal(
    widget_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget = widget_svc.get_widget(widget_id, uid(current_user))
    ctx = widget_svc.widget_data(widget, user_id=uid(current_user))
    return request.app.state.templates.TemplateResponse(
        request,
        "components/dashboard/edit_widget_modal.html",
        ctx,
    )


@router.put("/dashboard/widgets/{widget_id}")
async def update_widget(
    widget_id: int,
    size: str = Form(),
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget_svc.update_widget(widget_id, uid(current_user), WidgetSize(size))
    return Response(
        status_code=204,
        headers={"HX-Trigger": f"widgetRefresh-{widget_id}"},
    )


@router.delete("/dashboard/widgets/{widget_id}", response_class=HTMLResponse)
async def remove_widget(
    widget_id: int,
    current_user: User = Depends(get_current_user),
    widget_svc: DashboardWidgetService = Depends(get_dashboard_widget_service),
):
    widget_svc.delete_widget(widget_id, uid(current_user))
    return HTMLResponse(status_code=200)
