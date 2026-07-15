from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from salus.dependencies import (
    get_api_token_service,
    get_current_user,
    get_user_service,
)
from salus.exceptions import ApiError, ConflictError
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.api_token import ApiTokenService
from salus.services.user import UserService

router = APIRouter(prefix="/api/v1")


class _PasswordChangeBody(BaseModel):
    current_password: str
    new_password: str


class _TokenCreateBody(BaseModel):
    label: str
    scopes: str = ""


class _ThemeBody(BaseModel):
    theme: str


# ---------------------------------------------------------------------------
# Account
# ---------------------------------------------------------------------------


@router.get("/settings/account")
async def api_settings_account(
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    user_id = uid(current_user)
    identities = user_svc.list_identities(user_id)
    api_tokens = api_token_svc.list_tokens(user_id)

    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "display_name": current_user.display_name,
            "is_admin": current_user.is_admin,
            "is_active": current_user.is_active,
            "theme": current_user.theme,
            "locale": current_user.locale,
            "onboarding_dismissed": current_user.onboarding_dismissed,
            "created_at": current_user.created_at.isoformat()
            if current_user.created_at
            else None,
        },
        "identities": [
            {
                "id": i.id,
                "provider": i.provider,
                "provider_user_id": i.provider_user_id,
            }
            for i in identities
        ],
        "api_tokens": [
            {
                "id": t.id,
                "label": t.label,
                "token_prefix": t.token_prefix,
                "scopes": t.scopes,
                "is_active": t.is_active,
                "last_used_at": t.last_used_at.isoformat()
                if t.last_used_at
                else None,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in api_tokens
        ],
    }


# ---------------------------------------------------------------------------
# Password
# ---------------------------------------------------------------------------


@router.post("/settings/password")
async def api_change_password(
    body: _PasswordChangeBody,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
):
    try:
        user_svc.change_password(
            uid(current_user), body.current_password, body.new_password
        )
    except ConflictError as exc:
        raise ApiError(code="wrong_password", message=exc.message, status_code=400)
    return {"message": "Password changed successfully"}


# ---------------------------------------------------------------------------
# API Tokens
# ---------------------------------------------------------------------------


@router.post("/settings/tokens", status_code=201)
async def api_create_token(
    body: _TokenCreateBody,
    current_user: User = Depends(get_current_user),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    plaintext, token = api_token_svc.create_token(
        uid(current_user), body.label, body.scopes
    )
    return {
        "token": plaintext,
        "prefix": token.token_prefix,
        "scopes": token.scopes,
    }


@router.delete("/settings/tokens/{token_id}", status_code=204)
async def api_revoke_token(
    token_id: str,
    current_user: User = Depends(get_current_user),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    api_token_svc.revoke(token_id, uid(current_user))
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------


@router.put("/settings/theme", status_code=204)
async def api_set_theme(
    body: _ThemeBody,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
):
    user_svc.set_theme(uid(current_user), body.theme)
    return Response(status_code=204)
