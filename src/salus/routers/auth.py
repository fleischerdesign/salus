from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from salus.config import settings
from salus.dependencies import (
    TOKEN_COOKIE_NAME,
    get_auth_service,
    get_current_user_optional,
    get_user_service,
)
from salus.exceptions import ConflictError, InvalidCredentialsError
from salus.models.user import User
from salus.services.auth.service import AuthService
from salus.services.user import UserService

router = APIRouter()


def _set_auth_cookie(response: RedirectResponse, token: str) -> None:
    response.set_cookie(
        key=TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=settings.jwt_expire_minutes * 60,
        samesite="lax",
    )


def _redirect_if_authenticated(current_user: User | None) -> RedirectResponse | None:
    if current_user is not None:
        return RedirectResponse(url="/", status_code=303)
    return None


def _render_login_template(request: Request, extra: dict | None = None) -> HTMLResponse:
    context = {"error": None, "current_user": None, "ldap_mode": False}
    if extra:
        context.update(extra)
    return request.app.state.templates.TemplateResponse(
        request, "pages/login.html", context
    )


def _register_error(request: Request, message: str) -> HTMLResponse:
    return request.app.state.templates.TemplateResponse(
        request,
        "pages/register.html",
        {"error": message, "current_user": None},
        status_code=409,
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    if redirect := _redirect_if_authenticated(current_user):
        return redirect
    return _render_login_template(request)


@router.post("/login")
async def login(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    auth_svc: AuthService = Depends(get_auth_service),
):
    try:
        token, user = auth_svc.login_local(username=username, password=password)
    except InvalidCredentialsError:
        return _render_login_template(
            request, {"error": "Invalid username or password"}
        )

    response = RedirectResponse(url="/", status_code=303)
    _set_auth_cookie(response, token)
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    if redirect := _redirect_if_authenticated(current_user):
        return redirect
    return request.app.state.templates.TemplateResponse(
        request, "pages/register.html", {"error": None, "current_user": None}
    )


@router.post("/register")
async def register(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    email: str | None = Form(None),
    display_name: str | None = Form(None),
    user_svc: UserService = Depends(get_user_service),
    auth_svc: AuthService = Depends(get_auth_service),
):
    try:
        user = user_svc.register(
            username=username,
            password=password,
            email=email or None,
            display_name=display_name or None,
        )
    except ConflictError as exc:
        return _register_error(request, exc.message)

    token = auth_svc.create_token_for_user(user)
    response = RedirectResponse(url="/", status_code=303)
    _set_auth_cookie(response, token)
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=303)
    response.delete_cookie(TOKEN_COOKIE_NAME)
    return response


@router.get("/ldap", response_class=HTMLResponse)
async def ldap_login_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    if redirect := _redirect_if_authenticated(current_user):
        return redirect
    return _render_login_template(request, {"ldap_mode": True})


@router.post("/ldap")
async def ldap_login(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    auth_svc: AuthService = Depends(get_auth_service),
):
    try:
        token, user = auth_svc.login_ldap(username=username, password=password)
    except InvalidCredentialsError:
        return _render_login_template(
            request, {"error": "LDAP authentication failed", "ldap_mode": True}
        )

    response = RedirectResponse(url="/", status_code=303)
    _set_auth_cookie(response, token)
    return response


@router.get("/oidc/{provider}")
async def oidc_login(
    provider: str,
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
):
    redirect_uri = str(request.url_for("oidc_callback", provider=provider))
    try:
        auth_url = auth_svc.get_oidc_authorization_url(provider, redirect_uri)
    except ValueError:
        return HTMLResponse(status_code=404, content=f"Unknown provider: {provider}")
    return RedirectResponse(url=auth_url)


@router.get("/oidc/{provider}/callback")
async def oidc_callback(
    provider: str,
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
):
    oidc_provider = auth_svc.get_oidc_provider(provider)
    if oidc_provider is None:
        return HTMLResponse(status_code=404, content=f"Unknown provider: {provider}")

    user = await oidc_provider.authenticate(request)
    if user is None:
        return HTMLResponse(status_code=401, content="OIDC authentication failed")

    token = auth_svc.create_token_for_user(user)
    response = RedirectResponse(url="/", status_code=303)
    _set_auth_cookie(response, token)
    return response
