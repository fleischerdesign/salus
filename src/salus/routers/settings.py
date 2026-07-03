from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from salus.dependencies import (
    get_api_token_service,
    get_current_user,
    get_metric_type_service,
    get_user_service,
    get_asymmetric_share_service,
)
from salus.exceptions import ConflictError
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.api_token import ApiTokenService
from salus.services.metric_type import MetricTypeService
from salus.services.user import UserService
from salus.services.asymmetric_share import AsymmetricShareService

router = APIRouter()


def _settings_context(
    request: Request,
    current_user: User,
    user_svc: UserService,
    metric_svc: MetricTypeService,
    api_token_svc: ApiTokenService | None = None,
    share_svc: AsymmetricShareService | None = None,
    **extra,
) -> dict:
    user_id = uid(current_user)
    identities = user_svc.list_identities(user_id)
    metrics = metric_svc.find_all(user_id)
    connected_providers = [i.provider for i in identities]
    api_tokens = api_token_svc.list_tokens(user_id) if api_token_svc else []
    
    recipients = []
    shares = []
    if share_svc:
        recipients = share_svc.list_recipients(user_id)
        shares = share_svc.list_shares(user_id)
        
    return {
        "current_user": current_user,
        "identities": identities,
        "connected_providers": connected_providers,
        "metrics": metrics,
        "api_tokens": api_tokens,
        "recipients": recipients,
        "shares": shares,
        "error": None,
        "success": None,
        **extra,
    }


def _render_settings_tab(request: Request, tab_name: str, context: dict):
    context["active_tab"] = tab_name
    if request.headers.get("HX-Request"):
        return request.app.state.templates.TemplateResponse(
            request, f"pages/settings_tabs/{tab_name}.html", context
        )
    return request.app.state.templates.TemplateResponse(
        request, "pages/settings.html", context
    )


@router.get("", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    context = _settings_context(request, current_user, user_svc, metric_svc, api_token_svc)
    return _render_settings_tab(request, "account", context)


@router.get("/privacy", response_class=HTMLResponse)
async def settings_privacy_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    context = _settings_context(request, current_user, user_svc, metric_svc, api_token_svc)
    return _render_settings_tab(request, "privacy", context)


@router.get("/shares", response_class=HTMLResponse)
async def settings_shares_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
    share_svc: AsymmetricShareService = Depends(get_asymmetric_share_service),
):
    context = _settings_context(request, current_user, user_svc, metric_svc, api_token_svc, share_svc)
    return _render_settings_tab(request, "shares", context)


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
        return _render_settings_tab(request, "account", context)

    context = _settings_context(
        request, current_user, user_svc, metric_svc, api_token_svc,
        success="Password changed successfully.",
    )
    return _render_settings_tab(request, "account", context)


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


@router.post("/theme")
async def set_theme(
    theme: Annotated[str, Form()],
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
):
    user_svc.set_theme(uid(current_user), theme)
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/locale")
async def set_locale(
    locale: Annotated[str, Form()],
):
    response = RedirectResponse(url="/settings", status_code=303)
    response.set_cookie("salus_locale", locale, max_age=31536000, httponly=True)
    return response
