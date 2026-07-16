from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse

from salus.config import settings
from salus.dependencies import (
    TOKEN_COOKIE_NAME,
    get_auth_service,
    get_current_user,
    get_user_service,
    limiter,
)
from salus.exceptions import ApiError, ConflictError, InvalidCredentialsError
from salus.schemas.user import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    AuthConfigResponse,
)
from salus.services.auth.service import AuthService
from salus.services.user import UserService

router = APIRouter(prefix="/api/v1")


def _set_session_cookie(response, token: str) -> None:
    response.set_cookie(
        key=TOKEN_COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.is_production,
        max_age=settings.jwt_expire_minutes * 60,
        samesite="lax",
    )


def _json_auth_response(token: str, user) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content=TokenResponse(
            token=token,
            user=UserResponse.model_validate(user),
        ).model_dump(mode="json"),
    )


@router.post("/auth/login")
@limiter.limit("5/minute")
async def api_login(
    request: Request,
    body: LoginRequest,
    auth_svc: AuthService = Depends(get_auth_service),
):
    try:
        token, user = auth_svc.login_local(username=body.username, password=body.password)
    except InvalidCredentialsError:
        raise ApiError(code="invalid_credentials", message="Invalid username or password", status_code=401)

    response = _json_auth_response(token, user)
    _set_session_cookie(response, token)
    return response


@router.post("/auth/register")
@limiter.limit("3/minute")
async def api_register(
    request: Request,
    body: RegisterRequest,
    user_svc: UserService = Depends(get_user_service),
    auth_svc: AuthService = Depends(get_auth_service),
):
    try:
        user = user_svc.register(
            username=body.username,
            password=body.password,
            email=body.email,
            display_name=body.display_name,
        )
    except ConflictError:
        raise

    token = auth_svc.create_token_for_user(user)
    response = _json_auth_response(token, user)
    _set_session_cookie(response, token)
    return response


@router.post("/auth/logout")
async def api_logout():
    response = JSONResponse(status_code=204, content=None)
    response.delete_cookie(TOKEN_COOKIE_NAME)
    return response


@router.get("/auth/me", response_model=UserResponse)
async def api_me(current_user=Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post("/auth/ldap")
@limiter.limit("5/minute")
async def api_ldap(
    request: Request,
    body: LoginRequest,
    auth_svc: AuthService = Depends(get_auth_service),
):
    try:
        token, user = auth_svc.login_ldap(username=body.username, password=body.password)
    except InvalidCredentialsError:
        raise ApiError(code="ldap_failed", message="LDAP authentication failed", status_code=401)

    response = _json_auth_response(token, user)
    _set_session_cookie(response, token)
    return response


@router.get("/auth/oidc/{provider}")
async def api_oidc_authorize(
    provider: str,
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
):
    redirect_uri = str(request.url_for("oidc_callback", provider=provider))
    try:
        auth_url = auth_svc.get_oidc_authorization_url(provider, redirect_uri)
    except ValueError:
        raise ApiError(code="unknown_provider", message=f"Unknown provider: {provider}", status_code=404)
    return JSONResponse(content={"authorization_url": auth_url})


@router.get("/auth/oidc/{provider}/login")
async def api_oidc_login(
    provider: str,
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
):
    redirect_uri = str(request.url_for("oidc_callback", provider=provider))
    try:
        auth_url = auth_svc.get_oidc_authorization_url(provider, redirect_uri)
    except ValueError:
        raise ApiError(code="unknown_provider", message=f"Unknown provider: {provider}", status_code=404)
    return RedirectResponse(url=auth_url)


@router.get("/auth/oidc/{provider}/callback", name="oidc_callback")
async def api_oidc_callback(
    provider: str,
    request: Request,
    auth_svc: AuthService = Depends(get_auth_service),
):
    oidc_provider = auth_svc.get_oidc_provider(provider)
    if oidc_provider is None:
        raise ApiError(code="unknown_provider", message=f"Unknown provider: {provider}", status_code=404)

    user = await oidc_provider.authenticate(request)
    if user is None:
        raise ApiError(code="oidc_failed", message="OIDC authentication failed", status_code=401)

    token = auth_svc.create_token_for_user(user)
    response = RedirectResponse(url="/", status_code=303)
    _set_session_cookie(response, token)
    return response


@router.get("/auth/config", response_model=AuthConfigResponse)
async def api_auth_config(
    auth_svc: AuthService = Depends(get_auth_service),
):
    providers = auth_svc.get_configured_oidc_providers()
    return AuthConfigResponse(oidc_providers=providers)

