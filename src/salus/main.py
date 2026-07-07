import logging
import os
import traceback
from contextlib import asynccontextmanager
from contextvars import ContextVar

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import StrictUndefined
from starlette.templating import Jinja2Templates

from salus.config import settings as app_settings
from salus.database import Session, engine
from salus.exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from salus.jinja2_ext import AutoImportLoader, render_attrs
from salus.models import system_config  # noqa: F401
from salus.models.insight import Insight as InsightModel  # noqa: F401
from salus.repositories.system_config import SystemConfigRepository
from salus.routers import (
    admin,
    analytics,
    api,
    auth,
    circadian,
    dashboard,
    design_system,
    entries,
    export,
    goals,
    insight,
    onboarding,
    settings,
    webhook,
    sharing,
    workout,
    asymmetric_share,
    open_science,
    notification,
)
from salus.services.config import ConfigService
from salus.services.i18n import translate

locale_ctx: ContextVar[str] = ContextVar("salus_locale", default="en")


log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


NAV_ITEMS = [
    {"path": "/", "icon": "dashboard", "label": "Dashboard", "exact": True},
    {"path": "/entries", "icon": "description", "label": "Logbook"},
    {"path": "/analytics", "icon": "bar_chart", "label": "Analytics"},
    {"path": "/goals", "icon": "track_changes", "label": "Goals"},
    {
        "label": "Workouts",
        "icon": "fitness_center",
        "children": [
            {"path": "/workouts/plans", "icon": "assignment", "label": "Plans"},
            {"path": "/workouts/exercises", "icon": "list", "label": "Exercises"},
            {
                "path": "/workouts/sessions/active",
                "icon": "play_circle",
                "label": "Active",
            },
        ],
    },
    {
        "label": "Coach",
        "icon": "psychology",
        "children": [
            {"path": "/circadian", "icon": "light_mode", "label": "Circadian"},
            {"path": "/insights", "icon": "chat", "label": "Chat"},
        ],
    },
    {
        "label": "Community",
        "icon": "group",
        "children": [
            {"path": "/sharing/feed", "icon": "feed", "label": "Feed"},
            {
                "path": "/sharing/leaderboard",
                "icon": "leaderboard",
                "label": "Leaderboard",
            },
            {
                "path": "/sharing/connections",
                "icon": "contacts",
                "label": "Connections",
            },
            {
                "path": "/sharing/access-log",
                "icon": "visibility",
                "label": "Access Log",
            },
        ],
    },
]


def get_translation_context(request: Request):
    locale = request.cookies.get("salus_locale")
    if not locale:
        accept_lang = request.headers.get("Accept-Language", "")
        locale = "de" if "de" in accept_lang.lower() else "en"
    return {"_": lambda text: translate(text, locale), "current_locale": locale}


async def i18n_middleware(request: Request, call_next):
    locale = request.cookies.get("salus_locale")
    if not locale:
        accept_lang = request.headers.get("Accept-Language", "")
        locale = "de" if "de" in accept_lang.lower() else "en"
    locale_ctx.set(locale)
    response = await call_next(request)
    return response


def _translate(text: str) -> str:
    return translate(text, locale_ctx.get())


def get_nav_context(request: Request):
    current_path = request.url.path
    items = []

    all_items = list(NAV_ITEMS)
    plugin_items = []
    if (
        hasattr(request.app, "state")
        and hasattr(request.app.state, "plugin_manager")
        and request.app.state.plugin_manager
    ):
        for nav_hook in request.app.state.plugin_manager.registry.navigations:
            try:
                plugin_items.extend(nav_hook.get_navigation_items())
            except Exception as e:
                logging.error(f"Error fetching navigation items from plugin: {e}")

    if plugin_items:
        all_items.append(
            {"label": "Plugins", "icon": "extension", "children": plugin_items}
        )

    for item in all_items:
        if "children" in item:
            children_with_active = []
            parent_active = False
            for child in item["children"]:
                is_active = (
                    current_path == child["path"]
                    if child.get("exact")
                    else current_path.startswith(child["path"])
                )
                if is_active:
                    parent_active = True
                children_with_active.append({**child, "active": is_active})
            items.append(
                {**item, "children": children_with_active, "active": parent_active}
            )
        else:
            is_active = (
                current_path == item["path"]
                if item.get("exact")
                else current_path.startswith(item["path"])
            )
            items.append(
                {
                    **item,
                    "active": is_active,
                    "children": None,
                }
            )
    return {"nav_items": items}


def get_plugin_assets_context(request: Request):
    custom_css = []
    custom_js = []
    if (
        hasattr(request.app, "state")
        and hasattr(request.app.state, "plugin_manager")
        and request.app.state.plugin_manager
    ):
        for style_hook in request.app.state.plugin_manager.registry.custom_styles:
            try:
                css = style_hook.get_custom_css()
                if css:
                    custom_css.append(css)
                js = style_hook.get_custom_js()
                if js:
                    custom_js.append(js)
            except Exception as e:
                logging.error(f"Error fetching style/js from plugin: {e}")
    return {
        "plugin_custom_css": "\n".join(custom_css),
        "plugin_custom_js": "\n".join(custom_js),
    }


templates = Jinja2Templates(
    directory="src/salus/templates",
    context_processors=[
        get_translation_context,
        get_nav_context,
        get_plugin_assets_context,
    ],
)
templates.env.undefined = StrictUndefined
templates.env.globals["settings"] = app_settings
templates.env.globals["_"] = _translate
templates.env.filters["render_attrs"] = render_attrs
if templates.env.loader is not None:
    templates.env.loader = AutoImportLoader(templates.env.loader)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-build component CSS on startup
    import sys
    from pathlib import Path

    root_dir = Path(__file__).resolve().parent.parent.parent
    if str(root_dir) not in sys.path:
        sys.path.append(str(root_dir))
    try:
        from tools.build_components import main as build_css

        build_css()
    except Exception as e:
        logging.error(f"Failed to auto-build component CSS on startup: {e}")

    # Load plugins first to register translations, lifecycle hooks, routes, and schemas

    from salus.repositories.unit_of_work import SqlUnitOfWork
    from salus.services.plugin.manager import PluginManager
    from salus.services.i18n import register_plugin_translations
    from fastapi import APIRouter

    startup_session = Session(engine)
    uow = SqlUnitOfWork(startup_session)
    plugin_manager = PluginManager(plugins_dir="src/salus/plugins", uow=uow)

    try:
        plugin_manager.discover_and_load_all()
    except Exception as e:
        logging.error(f"Error loading plugins: {e}", exc_info=True)

    app.state.plugin_manager = plugin_manager

    # Register translations from HookTranslation
    for trans_hook in plugin_manager.registry.translations:
        try:
            register_plugin_translations(trans_hook.get_translations())
        except Exception as e:
            logging.error(f"Error registering plugin translations: {e}")

    # Trigger HookApplicationLifecycle.on_startup
    for lifecycle_hook in plugin_manager.registry.lifecycles:
        try:
            lifecycle_hook.on_startup()
        except Exception as e:
            logging.error(f"Error in plugin startup hook: {e}")

    # Run programmatic migrations
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect

    alembic_cfg = Config("alembic.ini")
    inspector = inspect(engine)
    if (
        "user" in inspector.get_table_names()
        and "alembic_version" not in inspector.get_table_names()
    ):
        command.stamp(alembic_cfg, "head")
    else:
        command.upgrade(alembic_cfg, "head")

    session = Session(engine)
    try:
        ConfigService(SystemConfigRepository(session)).seed_defaults()
    finally:
        session.close()
        startup_session.close()

    # Register dynamic API routes
    plugin_router = APIRouter(prefix="/api/plugins")
    for pr in plugin_manager.registry.api_routers:
        try:
            pr.register_routes(plugin_router)
        except Exception as e:
            logging.error(f"Error registering API routes for plugin: {e}")
    app.include_router(plugin_router)

    app.state.templates = templates
    yield

    # Trigger HookApplicationLifecycle.on_shutdown
    for lifecycle_hook in plugin_manager.registry.lifecycles:
        try:
            lifecycle_hook.on_shutdown()
        except Exception as e:
            logging.error(f"Error in plugin shutdown hook: {e}")

    plugin_manager.unload_all()


app = FastAPI(title="salus", lifespan=lifespan)
app.state.engine = engine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(i18n_middleware)


@app.get("/sw.js")
async def serve_service_worker():
    from fastapi.responses import FileResponse
    return FileResponse("src/salus/static/sw.js", media_type="application/javascript")


app.mount("/static", StaticFiles(directory="src/salus/static"), name="static")
app.include_router(dashboard.router)
app.include_router(entries.router, prefix="/entries")
app.include_router(webhook.router)
app.include_router(onboarding.router)
app.include_router(auth.router, prefix="/auth")
app.include_router(settings.router, prefix="/settings")
app.include_router(analytics.router)
app.include_router(goals.router, prefix="/goals")
app.include_router(api.router)
app.include_router(export.router)
app.include_router(admin.router)
app.include_router(insight.router, prefix="/insights")
app.include_router(sharing.router)
app.include_router(workout.router)
app.include_router(asymmetric_share.router)
app.include_router(open_science.router)
app.include_router(circadian.router)
app.include_router(design_system.router)
app.include_router(notification.router)


def is_api_request(request: Request) -> bool:
    return (
        request.url.path.startswith("/api/")
        or request.url.path.startswith("/webhook")
        or request.url.path.startswith("/.well-known/")
    )


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    if is_api_request(request):
        return JSONResponse(status_code=404, content={"error": exc.message})
    return HTMLResponse(status_code=404, content=exc.message)


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    if is_api_request(request):
        return JSONResponse(status_code=409, content={"error": exc.message})
    return HTMLResponse(status_code=409, content=exc.message)


@app.exception_handler(AuthenticationError)
async def auth_error_handler(request: Request, exc: AuthenticationError):
    if is_api_request(request):
        return JSONResponse(status_code=401, content={"error": exc.message})
    return RedirectResponse(url="/auth/login", status_code=303)


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    if is_api_request(request):
        return JSONResponse(status_code=403, content={"error": exc.message})
    return RedirectResponse(url="/", status_code=303)


@app.exception_handler(404)
async def not_found_fallback(request: Request, exc: Exception):
    if is_api_request(request):
        return JSONResponse(status_code=404, content={"error": "Not Found"})
    return RedirectResponse(url="/", status_code=303)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.error(
        "Unhandled exception on %s %s:\n%s",
        request.method,
        request.url.path,
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )
    if is_api_request(request):
        return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
    return HTMLResponse(status_code=500, content="<h1>500 — Internal Server Error</h1>")
