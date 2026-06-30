from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse

from salus.dependencies import (
    get_api_token_service,
    get_current_user,
    get_metric_type_service,
    get_user_service,
)
from salus.exceptions import ConflictError
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.api_token import ApiTokenService
from salus.services.metric_type import MetricTypeService
from salus.services.user import UserService

router = APIRouter()


def _settings_context(
    request: Request,
    current_user: User,
    user_svc: UserService,
    metric_svc: MetricTypeService,
    api_token_svc: ApiTokenService | None = None,
    **extra,
) -> dict:
    user_id = uid(current_user)
    identities = user_svc.list_identities(user_id)
    metrics = metric_svc.find_all(user_id)
    connected_providers = [i.provider for i in identities]
    api_tokens = api_token_svc.list_tokens(user_id) if api_token_svc else []
    return {
        "current_user": current_user,
        "identities": identities,
        "connected_providers": connected_providers,
        "metrics": metrics,
        "api_tokens": api_tokens,
        "error": None,
        "success": None,
        **extra,
    }


@router.get("", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    context = _settings_context(request, current_user, user_svc, metric_svc, api_token_svc)
    return request.app.state.templates.TemplateResponse(request, "pages/settings.html", context)


@router.post("/change-password")
async def change_password(
    request: Request,
    current_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    try:
        user_svc.change_password(uid(current_user), current_password, new_password)
    except ConflictError as exc:
        context = _settings_context(
            request, current_user, user_svc, metric_svc, api_token_svc,
            error=exc.message,
        )
        return request.app.state.templates.TemplateResponse(request, "pages/settings.html", context)

    context = _settings_context(
        request, current_user, user_svc, metric_svc, api_token_svc,
        success="Password changed successfully.",
    )
    return request.app.state.templates.TemplateResponse(request, "pages/settings.html", context)


@router.get("/api-tokens/new", response_class=HTMLResponse)
async def new_token_form(request: Request):
    return request.app.state.templates.TemplateResponse(request, "components/api_token_form.html", {})


@router.post("/api-tokens", response_class=HTMLResponse)
async def create_api_token(
    request: Request,
    label: Annotated[str, Form()],
    scopes: list[str] = Form(default=[]),
    current_user: User = Depends(get_current_user),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    scope_str = " ".join(scopes)
    plaintext, _ = api_token_svc.create_token(uid(current_user), label, scope_str)
    return request.app.state.templates.TemplateResponse(
        request,
        "components/api_token_generated.html",
        {"plaintext_token": plaintext},
    )


@router.delete("/api-tokens/{token_id}", response_class=HTMLResponse)
async def revoke_api_token(
    token_id: int,
    current_user: User = Depends(get_current_user),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    api_token_svc.revoke(token_id, uid(current_user))
    return HTMLResponse(status_code=200)
