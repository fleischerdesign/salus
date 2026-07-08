from typing import Annotated
import os
import re

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from salus.dependencies import (
    get_api_token_service,
    get_current_user,
    get_metric_type_service,
    get_user_service,
    get_asymmetric_share_service,
    get_backup_service,
)
from salus.exceptions import ConflictError
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.api_token import ApiTokenService
from salus.services.metric_type import MetricTypeService
from salus.services.user import UserService
from salus.services.asymmetric_share import AsymmetricShareService
from salus.services.backup.service import BackupService

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
    context = _settings_context(
        request, current_user, user_svc, metric_svc, api_token_svc
    )
    return _render_settings_tab(request, "account", context)


@router.get("/privacy", response_class=HTMLResponse)
async def settings_privacy_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
):
    context = _settings_context(
        request, current_user, user_svc, metric_svc, api_token_svc
    )
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
    context = _settings_context(
        request, current_user, user_svc, metric_svc, api_token_svc, share_svc
    )
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
            request,
            current_user,
            user_svc,
            metric_svc,
            api_token_svc,
            error=exc.message,
        )
        return _render_settings_tab(request, "account", context)

    context = _settings_context(
        request,
        current_user,
        user_svc,
        metric_svc,
        api_token_svc,
        success="Password changed successfully.",
    )
    return _render_settings_tab(request, "account", context)


@router.get("/api-tokens/new", response_class=HTMLResponse)
async def new_token_form(request: Request):
    return request.app.state.templates.TemplateResponse(
        request, "components/api_token_form.html", {}
    )


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
    request: Request,
    theme: Annotated[str, Form()],
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
):
    user_svc.set_theme(uid(current_user), theme)
    if request.headers.get("HX-Request"):
        from fastapi import Response
        return Response(status_code=204)
    return RedirectResponse(url="/settings", status_code=303)


@router.post("/locale")
async def set_locale(
    locale: Annotated[str, Form()],
):
    response = RedirectResponse(url="/settings", status_code=303)
    response.set_cookie("salus_locale", locale, max_age=31536000, httponly=True)
    return response


# ---------------------------------------------------------------------------
# Backups
# ---------------------------------------------------------------------------

@router.get("/backups", response_class=HTMLResponse)
async def settings_backups_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
    backup_svc: BackupService = Depends(get_backup_service),
    success: str | None = None,
    error: str | None = None,
):
    from salus.dependencies import require_admin
    # Ensure only admins can access backups
    require_admin(current_user)

    backups = []
    error_msg = error
    
    try:
        raw_backups = backup_svc.provider.list_backups()
        
        # Sort backups by parsed date in descending order
        parsed_backups = []
        for fname in raw_backups:
            # Parse size
            size_bytes = 0
            from salus.services.backup.providers import LocalBackupProvider
            if isinstance(backup_svc.provider, LocalBackupProvider):
                try:
                    size_bytes = os.path.getsize(os.path.join(backup_svc.provider.directory, fname))
                except Exception:
                    pass
            
            # Format size
            if size_bytes > 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
            elif size_bytes > 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes} B" if size_bytes > 0 else "--"

            # Parse datetime from filename salus_backup_YYYY-MM-DD_HH-MM-SS.enc
            created_at_str = "--"
            match = re.match(r"salus_backup_(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})\.enc", fname)
            if match:
                created_at_str = f"{match.group(1)} {match.group(2)}:{match.group(3)}:{match.group(4)}"

            parsed_backups.append({
                "filename": fname,
                "created_at": created_at_str,
                "size_str": size_str,
                "raw_date": created_at_str
            })
            
        parsed_backups.sort(key=lambda x: x["raw_date"], reverse=True)
        backups = parsed_backups
    except Exception as e:
        error_msg = f"Failed to list backups: {str(e)}"

    from salus.config import settings as app_settings
    
    # Determine local directory path or WebDAV URL for display
    from salus.services.backup.providers import LocalBackupProvider
    if isinstance(backup_svc.provider, LocalBackupProvider):
        storage_location = backup_svc.provider.directory
    else:
        storage_location = getattr(backup_svc.provider, "url", "Remote WebDAV Storage")

    context = _settings_context(
        request, current_user, user_svc, metric_svc, api_token_svc,
        backups=backups,
        backup_provider=app_settings.backup_provider,
        backup_password_configured=bool(app_settings.backup_password),
        storage_location=storage_location,
        error=error_msg,
        success=success,
    )
    return _render_settings_tab(request, "backups", context)


@router.post("/backups/create", response_class=HTMLResponse)
async def trigger_backup_post(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
    backup_svc: BackupService = Depends(get_backup_service),
):
    from salus.dependencies import require_admin
    require_admin(current_user)

    success_msg = None
    error_msg = None
    
    try:
        filename = backup_svc.run_backup()
        success_msg = f"Backup '{filename}' created and uploaded successfully."
    except Exception as e:
        error_msg = f"Backup failed: {str(e)}"

    # Re-render list
    return await settings_backups_page(
        request=request,
        current_user=current_user,
        user_svc=user_svc,
        metric_svc=metric_svc,
        api_token_svc=api_token_svc,
        backup_svc=backup_svc,
        success=success_msg,
        error=error_msg,
    )


@router.post("/backups/restore/{filename}", response_class=HTMLResponse)
async def restore_backup_post(
    request: Request,
    filename: str,
    current_user: User = Depends(get_current_user),
    backup_svc: BackupService = Depends(get_backup_service),
):
    from salus.dependencies import require_admin
    require_admin(current_user)
    
    from salus.config import settings as app_settings
    if not app_settings.database_url.startswith("sqlite:///"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Database restoration is only supported for SQLite databases.")

    db_path = app_settings.database_url.replace("sqlite:///", "")
    
    try:
        backup_svc.restore_backup(filename, db_path)
        # Return a client-side reload triggers
        return HTMLResponse(
            content="<script>alert('Database successfully restored from backup! The page will now reload.'); window.location.reload();</script>"
        )
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Restoration failed: {str(e)}")


@router.delete("/backups/{filename}", response_class=HTMLResponse)
async def delete_backup_route(
    request: Request,
    filename: str,
    current_user: User = Depends(get_current_user),
    user_svc: UserService = Depends(get_user_service),
    metric_svc: MetricTypeService = Depends(get_metric_type_service),
    api_token_svc: ApiTokenService = Depends(get_api_token_service),
    backup_svc: BackupService = Depends(get_backup_service),
):
    from salus.dependencies import require_admin
    require_admin(current_user)

    try:
        backup_svc.provider.delete_backup(filename)
    except Exception:
        pass

    return await settings_backups_page(
        request=request,
        current_user=current_user,
        user_svc=user_svc,
        metric_svc=metric_svc,
        api_token_svc=api_token_svc,
        backup_svc=backup_svc,
    )
