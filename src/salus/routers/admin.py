from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse

from salus.config import settings
from salus.dependencies import (
    require_admin,
    get_admin_service,
    get_config_service,
    get_plugin_manager,
    get_backup_service,
)
from salus.models.user import User
from salus.services._helpers import uid
from salus.services.admin import AdminService
from salus.services.config import CATEGORY_ORDER, ConfigService
from salus.services.plugin import PluginManager
from salus.services.backup.service import BackupService

router = APIRouter()


def _admin_context(
    request: Request,
    current_user: User,
    admin_svc: AdminService,
    config_svc: ConfigService,
    plugin_mgr: PluginManager | None,
    backup_svc: BackupService,
) -> dict:
    stats = admin_svc.get_system_stats()
    storage = admin_svc.get_storage_stats()
    users = admin_svc.list_users_with_stats()
    tokens = admin_svc.list_all_tokens()
    config_by_cat: dict[str, list[dict]] = {}
    for item in config_svc.get_all():
        config_by_cat.setdefault(item["category"], []).append(item)

    plugins = plugin_mgr.get_discovered_plugins() if plugin_mgr else []
    
    backups = []
    if settings.backup_password:
        try:
            backups = backup_svc.provider.list_backups()
        except Exception:
            pass

    return {
        "current_user": current_user,
        "stats": stats,
        "storage": storage,
        "users": users,
        "tokens": tokens,
        "config_categories": CATEGORY_ORDER,
        "config_by_cat": config_by_cat,
        "plugins": plugins,
        "backups": backups,
        "settings": settings,
    }


def _render_admin_tab(request: Request, tab_name: str, context: dict):
    context["active_tab"] = tab_name
    if request.headers.get("HX-Request"):
        return request.app.state.templates.TemplateResponse(
            request, f"pages/admin_tabs/{tab_name}.html", context
        )
    return request.app.state.templates.TemplateResponse(
        request, "pages/admin.html", context
    )


@router.get("/admin", response_class=HTMLResponse)
async def admin_general_page(
    request: Request,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
    config_svc: ConfigService = Depends(get_config_service),
    plugin_mgr: PluginManager = Depends(get_plugin_manager),
    backup_svc: BackupService = Depends(get_backup_service),
):
    context = _admin_context(request, current_user, admin_svc, config_svc, plugin_mgr, backup_svc)
    return _render_admin_tab(request, "general", context)


@router.get("/admin/users", response_class=HTMLResponse)
async def admin_users_page(
    request: Request,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
    config_svc: ConfigService = Depends(get_config_service),
    plugin_mgr: PluginManager = Depends(get_plugin_manager),
    backup_svc: BackupService = Depends(get_backup_service),
):
    context = _admin_context(request, current_user, admin_svc, config_svc, plugin_mgr, backup_svc)
    return _render_admin_tab(request, "users", context)


@router.get("/admin/stats", response_class=HTMLResponse)
async def admin_stats_page(
    request: Request,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
    config_svc: ConfigService = Depends(get_config_service),
    plugin_mgr: PluginManager = Depends(get_plugin_manager),
    backup_svc: BackupService = Depends(get_backup_service),
):
    context = _admin_context(request, current_user, admin_svc, config_svc, plugin_mgr, backup_svc)
    return _render_admin_tab(request, "stats", context)


@router.get("/admin/plugins", response_class=HTMLResponse)
async def admin_plugins_page(
    request: Request,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
    config_svc: ConfigService = Depends(get_config_service),
    plugin_mgr: PluginManager = Depends(get_plugin_manager),
    backup_svc: BackupService = Depends(get_backup_service),
):
    context = _admin_context(request, current_user, admin_svc, config_svc, plugin_mgr, backup_svc)
    return _render_admin_tab(request, "plugins", context)


@router.post("/admin/users/{user_id}/toggle-admin")
async def admin_toggle_admin(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    admin_svc.toggle_admin(user_id)
    users = admin_svc.list_users_with_stats()
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/user_table.html",
        {"users": users, "current_user": current_user},
    )


@router.post("/admin/users/{user_id}/toggle-active")
async def admin_toggle_active(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    admin_svc.toggle_active(user_id)
    users = admin_svc.list_users_with_stats()
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/user_table.html",
        {"users": users, "current_user": current_user},
    )


@router.get("/admin/users/{user_id}/detail", response_class=HTMLResponse)
async def admin_user_detail(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    detail = admin_svc.get_user_detail(user_id)
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/user_detail.html",
        {"detail": detail},
    )


@router.delete("/admin/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    admin_svc.delete_user(user_id, uid(current_user))
    users = admin_svc.list_users_with_stats()
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/user_table.html",
        {"users": users, "current_user": current_user},
    )


@router.delete("/admin/tokens/{token_id}", response_class=HTMLResponse)
async def admin_revoke_token(
    token_id: int,
    request: Request,
    current_user: User = Depends(require_admin),
    admin_svc: AdminService = Depends(get_admin_service),
):
    admin_svc.revoke_token(token_id)
    tokens = admin_svc.list_all_tokens()
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/token_table.html",
        {"tokens": tokens},
    )


@router.get("/admin/config/{category}", response_class=HTMLResponse)
async def admin_config_category(
    category: str,
    request: Request,
    current_user: User = Depends(require_admin),
    config_svc: ConfigService = Depends(get_config_service),
):
    items = [i for i in config_svc.get_all() if i["category"] == category]
    for i in items:
        i.setdefault("editing", False)
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/config_table.html",
        {"config_items": items, "category": category},
    )


@router.get("/admin/config/{key}/edit", response_class=HTMLResponse)
async def admin_config_edit_form(
    key: str,
    request: Request,
    current_user: User = Depends(require_admin),
    config_svc: ConfigService = Depends(get_config_service),
):
    all_items = config_svc.get_all()
    item = next((i for i in all_items if i["key"] == key), None)
    if item is None:
        return HTMLResponse(status_code=404)
    category = item["category"]
    items = [i for i in all_items if i["category"] == category]
    for i in items:
        i["editing"] = i["key"] == key
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/config_table.html",
        {"config_items": items, "category": category},
    )


@router.get("/admin/config/{key}/reveal", response_class=HTMLResponse)
async def admin_config_reveal(
    key: str,
    request: Request,
    current_user: User = Depends(require_admin),
    config_svc: ConfigService = Depends(get_config_service),
):
    value = config_svc.get_resolved_value(key)
    return HTMLResponse(
        f'<span style="font:var(--font-body-sm);">{value}</span>'
        f'<button class="btn-ghost btn-sm" hx-get="/admin/config/{key}/edit" '
        f'hx-target="closest td" hx-swap="innerHTML" title="Hide">'
        f'<span class="material-symbols-outlined" style="font-size:16px;">visibility_off</span></button>'
    )


@router.put("/admin/config/{key}")
async def admin_config_update(
    key: str,
    request: Request,
    value: Annotated[str, Form()],
    current_user: User = Depends(require_admin),
    config_svc: ConfigService = Depends(get_config_service),
):
    config_svc.set(key, value)
    all_items = config_svc.get_all()
    item = next((i for i in all_items if i["key"] == key), None)
    if item is None:
        return HTMLResponse(status_code=404)
    category = item["category"]
    items = [i for i in all_items if i["category"] == category]
    for i in items:
        i.setdefault("editing", False)
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/config_table.html",
        {"config_items": items, "category": category},
    )


@router.get("/admin/plugins/upload-modal", response_class=HTMLResponse)
async def admin_upload_modal(
    request: Request,
    current_user: User = Depends(require_admin),
):
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/upload_modal.html",
        {}
    )


@router.post("/admin/plugins/{plugin_id}/toggle", response_class=HTMLResponse)
async def admin_toggle_plugin(
    plugin_id: str,
    request: Request,
    enable: bool = Form(False),
    current_user: User = Depends(require_admin),
    plugin_mgr: PluginManager | None = Depends(get_plugin_manager),
):
    if plugin_mgr:
        plugin_mgr.toggle_plugin(plugin_id, enable)
    plugins = plugin_mgr.get_discovered_plugins() if plugin_mgr else []
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/plugin_table.html",
        {"plugins": plugins}
    )


@router.post("/admin/plugins/upload", response_class=HTMLResponse)
async def admin_upload_plugin(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    plugin_mgr: PluginManager | None = Depends(get_plugin_manager),
):
    if plugin_mgr:
        try:
            content = await file.read()
            plugin_mgr.install_plugin(content)
        except Exception:
            pass
    plugins = plugin_mgr.get_discovered_plugins() if plugin_mgr else []
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/plugin_table.html",
        {"plugins": plugins}
    )


@router.delete("/admin/plugins/{plugin_id}", response_class=HTMLResponse)
async def admin_uninstall_plugin(
    plugin_id: str,
    request: Request,
    current_user: User = Depends(require_admin),
    plugin_mgr: PluginManager | None = Depends(get_plugin_manager),
):
    if plugin_mgr:
        plugin_mgr.uninstall_plugin(plugin_id)
    plugins = plugin_mgr.get_discovered_plugins() if plugin_mgr else []
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/plugin_table.html",
        {"plugins": plugins}
    )


@router.post("/admin/backups/run", response_class=HTMLResponse)
async def admin_run_backup(
    request: Request,
    current_user: User = Depends(require_admin),
    backup_svc: BackupService = Depends(get_backup_service),
):
    if settings.backup_password:
        try:
            backup_svc.run_backup()
        except Exception:
            pass
    backups = backup_svc.provider.list_backups() if settings.backup_password else []
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/backup_table.html",
        {
            "backups": backups,
            "settings": settings,
        },
    )


@router.delete("/admin/backups/{filename}", response_class=HTMLResponse)
async def admin_delete_backup(
    filename: str,
    request: Request,
    current_user: User = Depends(require_admin),
    backup_svc: BackupService = Depends(get_backup_service),
):
    if settings.backup_password:
        try:
            backup_svc.provider.delete_backup(filename)
        except Exception:
            pass
    backups = backup_svc.provider.list_backups() if settings.backup_password else []
    return request.app.state.templates.TemplateResponse(
        request,
        "components/admin/backup_table.html",
        {
            "backups": backups,
            "settings": settings,
        },
    )
