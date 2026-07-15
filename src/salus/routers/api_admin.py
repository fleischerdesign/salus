import logging
import os
import re

from fastapi import APIRouter, Depends, Response, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from salus.config import settings as app_settings
from salus.dependencies import (
    get_admin_service,
    get_backup_service,
    get_config_service,
    get_plugin_manager,
    require_admin,
)
from salus.exceptions import ApiError
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.admin import AdminService
from salus.services.backup.service import BackupService
from salus.services.config import ConfigService
from salus.services.plugin.manager import PluginManager

router = APIRouter(prefix="/api/v1/admin")

MAX_BACKUP_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_PLUGIN_SIZE = 50 * 1024 * 1024  # 50 MB

class _ConfigValueBody(BaseModel):
    value: str


class _ToggleBody(BaseModel):
    enable: bool = True


def _format_backup_size(filepath: str) -> str:
    try:
        size_bytes = os.path.getsize(filepath)
    except Exception:
        logging.getLogger(__name__).warning("Failed to get file size for %s", filepath)
        return "--"
    if size_bytes > 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    elif size_bytes > 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes} B"


def _list_backups(backup_svc: BackupService) -> list[dict]:
    backups = []
    if not app_settings.backup_password:
        return backups
    try:
        raw_backups = backup_svc.provider.list_backups()
        from salus.services.backup.providers import LocalBackupProvider

        parsed = []
        for fname in raw_backups:
            size_str = "--"
            if isinstance(backup_svc.provider, LocalBackupProvider):
                size_str = _format_backup_size(
                    os.path.join(backup_svc.provider.directory, fname)
                )
            created_at_str = "--"
            match = re.match(
                r"salus_backup_(\d{4}-\d{2}-\d{2})_(\d{2})-(\d{2})-(\d{2})\.enc",
                fname,
            )
            if match:
                created_at_str = (
                    f"{match.group(1)} {match.group(2)}:{match.group(3)}:{match.group(4)}"
                )
            parsed.append(
                {
                    "filename": fname,
                    "created_at": created_at_str,
                    "size_str": size_str,
                    "raw_date": created_at_str,
                }
            )
        parsed.sort(key=lambda x: x["raw_date"], reverse=True)
        backups = parsed
    except Exception:
        logging.getLogger(__name__).warning("Failed to parse backup listing filename", exc_info=True)
    return backups


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


class AdminStatsResponse(BaseModel):
    stats: dict
    storage: dict


class _ConfigItem(BaseModel):
    key: str
    value: str | None = None
    source: str | None = None
    description: str | None = None
    is_secret: bool = False
    category: str | None = None
    is_env_override: bool = False
    env_var_name: str | None = None
    db_has_value: bool = False


class _ConfigValueResponse(BaseModel):
    key: str
    value: str
    category: str | None = None
    description: str | None = None


@router.get("/stats", response_model=AdminStatsResponse)
async def api_admin_stats(
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    stats = admin_svc.get_system_stats()
    storage = admin_svc.get_storage_stats()
    return {
        "stats": stats,
        "storage": storage,
    }


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


class _AdminUserItem(BaseModel):
    id: str
    username: str
    email: str | None = None
    display_name: str | None = None
    is_admin: bool
    is_active: bool
    created_at: str | None = None
    measurement_count: int
    goal_count: int


@router.get("/users", response_model=list[_AdminUserItem])
async def api_admin_users(
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    users = admin_svc.list_users_with_stats()
    return [
        {
            "id": u["id"],
            "username": u["username"],
            "email": u["email"],
            "display_name": u["display_name"],
            "is_admin": u["is_admin"],
            "is_active": u["is_active"],
            "created_at": u["created_at"].isoformat() if u["created_at"] else None,
            "measurement_count": u["measurement_count"],
            "goal_count": u["goal_count"],
        }
        for u in users
    ]


@router.get("/users/{user_id}")
async def api_admin_user_detail(
    user_id: str,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    return admin_svc.get_user_detail(user_id)


@router.post("/users/{user_id}/toggle-admin", status_code=204)
async def api_admin_toggle_admin(
    user_id: str,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    admin_svc.toggle_admin(user_id)
    return Response(status_code=204)


@router.post("/users/{user_id}/toggle-active", status_code=204)
async def api_admin_toggle_active(
    user_id: str,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    admin_svc.toggle_active(user_id)
    return Response(status_code=204)


@router.delete("/users/{user_id}", status_code=204)
async def api_admin_delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    admin_svc.delete_user(user_id, uid(current_user))
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------


@router.delete("/tokens/{token_id}", status_code=204)
async def api_admin_revoke_token(
    token_id: str,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    admin_svc.revoke_token(token_id)
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@router.get("/config", response_model=list[_ConfigItem])
async def api_admin_config(
    current_user: User = Depends(require_admin),
    config_svc: ConfigService = Depends(get_config_service),
):
    return config_svc.get_all()


@router.put("/config/{key}")
async def api_admin_config_update(
    key: str,
    body: _ConfigValueBody,
    current_user: User = Depends(require_admin),
    config_svc: ConfigService = Depends(get_config_service),
):
    updated = config_svc.set(key, body.value)
    return {
        "key": updated.key,
        "value": updated.value,
        "category": updated.category,
        "description": updated.description,
    }


# ---------------------------------------------------------------------------
# Plugins
# ---------------------------------------------------------------------------


@router.get("/plugins")
async def api_admin_plugins(
    current_user: User = Depends(require_admin),
    plugin_mgr: PluginManager | None = Depends(get_plugin_manager),
):
    if plugin_mgr is None:
        return []
    return plugin_mgr.get_discovered_plugins()


@router.post("/plugins/{plugin_id}/toggle")
async def api_admin_toggle_plugin(
    plugin_id: str,
    body: _ToggleBody,
    current_user: User = Depends(require_admin),
    plugin_mgr: PluginManager | None = Depends(get_plugin_manager),
):
    if plugin_mgr is None:
        raise ApiError(code="unavailable", message="Plugin manager not available", status_code=500)
    plugin_mgr.toggle_plugin(plugin_id, body.enable)
    plugins = plugin_mgr.get_discovered_plugins()
    return plugins


@router.post("/plugins/upload")
async def api_admin_upload_plugin(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    plugin_mgr: PluginManager | None = Depends(get_plugin_manager),
):
    if plugin_mgr is None:
        raise ApiError(code="unavailable", message="Plugin manager not available", status_code=500)
    try:
        content = await file.read()
    except Exception as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    if len(content) > MAX_PLUGIN_SIZE:
        return JSONResponse(status_code=413, content={"error": f"Plugin file too large. Maximum size is {MAX_PLUGIN_SIZE // (1024 * 1024)} MB."})
    try:
        plugin_id = plugin_mgr.install_plugin(content)
    except Exception as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    plugins = plugin_mgr.get_discovered_plugins()
    return {"plugin_id": plugin_id, "plugins": plugins}


@router.delete("/plugins/{plugin_id}", status_code=204)
async def api_admin_uninstall_plugin(
    plugin_id: str,
    current_user: User = Depends(require_admin),
    plugin_mgr: PluginManager | None = Depends(get_plugin_manager),
):
    if plugin_mgr is None:
        raise ApiError(code="unavailable", message="Plugin manager not available", status_code=500)
    plugin_mgr.uninstall_plugin(plugin_id)
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Backups
# ---------------------------------------------------------------------------


@router.get("/backups")
async def api_admin_backups(
    current_user: User = Depends(require_admin),
    backup_svc: BackupService = Depends(get_backup_service),
):
    return _list_backups(backup_svc)


@router.post("/backups", status_code=201)
async def api_admin_create_backup(
    current_user: User = Depends(require_admin),
    backup_svc: BackupService = Depends(get_backup_service),
):
    if not app_settings.backup_password:
        return JSONResponse(
            status_code=400, content={"error": "Backup password not configured"}
        )
    try:
        filename = backup_svc.run_backup()
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})

    from salus.services.backup.providers import LocalBackupProvider

    size = "--"
    if isinstance(backup_svc.provider, LocalBackupProvider):
        size = _format_backup_size(
            os.path.join(backup_svc.provider.directory, filename)
        )
    return {"filename": filename, "size": size}


@router.delete("/backups/{filename}", status_code=204)
async def api_admin_delete_backup(
    filename: str,
    current_user: User = Depends(require_admin),
    backup_svc: BackupService = Depends(get_backup_service),
):
    try:
        backup_svc.provider.delete_backup(filename)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
    return Response(status_code=204)


@router.post("/backups/{filename}/restore")
async def api_admin_restore_backup(
    filename: str,
    current_user: User = Depends(require_admin),
    backup_svc: BackupService = Depends(get_backup_service),
):
    if not app_settings.database_url.startswith("sqlite:///"):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Database restoration is only supported for SQLite databases."
            },
        )
    if not app_settings.backup_password:
        return JSONResponse(
            status_code=400, content={"error": "Backup password not configured"}
        )
    db_path = app_settings.database_url.replace("sqlite:///", "")
    try:
        backup_svc.restore_backup(filename, db_path)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
    return {"message": f"Database restored from {filename}"}


@router.post("/backups/upload")
async def api_admin_upload_backup(
    backup_file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    backup_svc: BackupService = Depends(get_backup_service),
):
    if not backup_file.filename or not backup_file.filename.endswith(".enc"):
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid file type. Only .enc backup files are allowed."},
        )
    try:
        content = await backup_file.read()
    except Exception as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    if len(content) > MAX_BACKUP_SIZE:
        return JSONResponse(status_code=413, content={"error": f"Backup file too large. Maximum size is {MAX_BACKUP_SIZE // (1024 * 1024)} MB."})
    try:
        backup_svc.provider.upload_backup(backup_file.filename, content)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
    return {
        "message": f"Backup '{backup_file.filename}' uploaded successfully.",
        "backups": _list_backups(backup_svc),
    }
