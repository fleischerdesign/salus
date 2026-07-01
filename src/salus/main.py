import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from salus.config import settings as app_settings
from salus.database import Session, engine
from salus.exceptions import AuthenticationError, ConflictError, ForbiddenError, NotFoundError
from salus.models import system_config  # noqa: F401
from salus.models.insight import Insight as InsightModel  # noqa: F401
from salus.repositories.system_config import SystemConfigRepository
from salus.routers import admin, analytics, api, auth, dashboard, entries, export, goals, insight, metrics, onboarding, settings, webhook
from salus.services.config import ConfigService
from salus.services.i18n import translate

log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level),
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


NAV_ITEMS = [
    {"path": "/", "icon": "dashboard", "label": "Dashboard", "exact": True},
    {"path": "/analytics", "icon": "analytics", "label": "Analytics"},
    {"path": "/insights", "icon": "psychology", "label": "AI Coach"},
    {"path": "/goals", "icon": "track_changes", "label": "Goals"},
    {"path": "/metrics", "icon": "label", "label": "Metrics"},
    {"path": "/entries", "icon": "description", "label": "Entries"},
]


def get_translation_context(request: Request):
    locale = request.cookies.get("salus_locale")
    if not locale:
        accept_lang = request.headers.get("Accept-Language", "")
        locale = "de" if "de" in accept_lang.lower() else "en"
    return {
        "_": lambda text: translate(text, locale),
        "current_locale": locale
    }


def get_nav_context(request: Request):
    current_path = request.url.path
    items = []
    for item in NAV_ITEMS:
        is_active = (
            current_path == item["path"]
            if item.get("exact")
            else current_path.startswith(item["path"])
        )
        items.append({
            **item,
            "active": is_active
        })
    return {"nav_items": items}


templates = Jinja2Templates(
    directory="src/salus/templates",
    context_processors=[get_translation_context, get_nav_context]
)
templates.env.globals["settings"] = app_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run programmatic migrations on startup
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect

    alembic_cfg = Config("alembic.ini")
    inspector = inspect(engine)
    if "user" in inspector.get_table_names() and "alembic_version" not in inspector.get_table_names():
        command.stamp(alembic_cfg, "head")
    else:
        command.upgrade(alembic_cfg, "head")

    session = Session(engine)
    try:
        ConfigService(SystemConfigRepository(session)).seed_defaults()
    finally:
        session.close()
    app.state.templates = templates
    yield


app = FastAPI(title="salus", lifespan=lifespan)
app.state.engine = engine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="src/salus/static"), name="static")
app.include_router(dashboard.router)
app.include_router(metrics.router, prefix="/metrics")
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


def is_api_request(request: Request) -> bool:
    return request.url.path.startswith("/api/") or request.url.path.startswith("/webhook")


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
