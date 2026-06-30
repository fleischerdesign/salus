from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from salus.dependencies import get_current_user, get_metric_type_service, get_user_service
from salus.exceptions import ConflictError
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.metric_type import MetricTypeService
from salus.services.user import UserService

router = APIRouter()


@router.get("", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    user_id = uid(current_user)
    identities = user_svc.list_identities(user_id)
    metrics = metric_svc.find_all(user_id)
    connected_providers = [i.provider for i in identities]
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/settings.html",
        {
            "current_user": current_user,
            "identities": identities,
            "connected_providers": connected_providers,
            "metrics": metrics,
            "error": None,
            "success": None,
        },
    )


@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
):
    user_id = uid(current_user)
    identities = user_svc.list_identities(user_id)
    connected_providers = [i.provider for i in identities]
    metrics = metric_svc.find_all(user_id)

    try:
        user_svc.change_password(uid(current_user), current_password, new_password)
    except ConflictError as exc:
        return request.app.state.templates.TemplateResponse(
            request,
            "pages/settings.html",
            {
                "current_user": current_user,
                "identities": identities,
                "connected_providers": connected_providers,
                "metrics": metrics,
                "error": exc.message,
                "success": None,
            },
        )

    return request.app.state.templates.TemplateResponse(
        request,
        "pages/settings.html",
        {
            "current_user": current_user,
            "identities": identities,
            "connected_providers": connected_providers,
            "metrics": metrics,
            "error": None,
            "success": "Password changed successfully.",
        },
    )
