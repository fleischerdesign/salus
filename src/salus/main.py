import logging
import os
import traceback
from contextlib import asynccontextmanager
from contextvars import ContextVar

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from salus.config import settings
from salus.database import Session, engine
from salus.exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
)
from salus.models import system_config  # noqa: F401
from salus.models.insight import Insight as InsightModel  # noqa: F401
from salus.repositories.system_config import SystemConfigRepository
from salus.routers import (
    api,
    api_admin,
    api_auth,
    api_dashboard,
    api_dynamic,
    api_misc,
    api_settings,
    api_sharing,
    api_sync,
    asymmetric_share,
    export,
    open_science,
    sharing,
    webhook,
    workout,
)
from salus.services.config import ConfigService
from salus.services.event_bus import InMemoryEventBus
from salus.services.i18n import translate

locale_ctx: ContextVar[str] = ContextVar("salus_locale", default="en")


log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def _translate(text: str) -> str:
    return translate(text, locale_ctx.get())


async def i18n_middleware(request: Request, call_next):
    accept_lang = request.headers.get("Accept-Language", "")
    locale = "de" if "de" in accept_lang.lower() else "en"
    locale_ctx.set(locale)
    response = await call_next(request)
    return response


class SPAStaticFiles(StaticFiles):
    """Serves SvelteKit SPA build with fallback to index.html for client-side routing."""

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404 and not path.startswith(("api/", "webhook/", ".well-known/")) and not path.endswith((".js", ".css", ".png", ".svg", ".woff2", ".ico", ".json")):
                return await super().get_response("index.html", scope)
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    from fastapi import APIRouter

    from salus.repositories.unit_of_work import SqlUnitOfWork
    from salus.services.i18n import register_plugin_translations
    from salus.services.plugin.manager import PluginManager

    lifespan_engine = getattr(app.state, "engine", engine)
    startup_session = Session(lifespan_engine)
    uow = SqlUnitOfWork(startup_session)
    plugin_manager = PluginManager(plugins_dir="src/salus/plugins", uow=uow)

    try:
        plugin_manager.discover_and_load_all()
    except Exception as e:
        logging.error(f"Error loading plugins: {e}", exc_info=True)

    app.state.plugin_manager = plugin_manager
    app.state.event_bus = InMemoryEventBus()

    for trans_hook in plugin_manager.registry.translations:
        try:
            register_plugin_translations(trans_hook.get_translations())
        except Exception as e:
            logging.error(f"Error registering plugin translations: {e}")

    for lifecycle_hook in plugin_manager.registry.lifecycles:
        try:
            lifecycle_hook.on_startup()
        except Exception as e:
            logging.error(f"Error in plugin startup hook: {e}")

    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect

    alembic_cfg = Config("alembic.ini")
    inspector = inspect(lifespan_engine)
    if (
        "user" in inspector.get_table_names()
        and "alembic_version" not in inspector.get_table_names()
    ):
        command.stamp(alembic_cfg, "head")
    else:
        command.upgrade(alembic_cfg, "head")

    session = Session(lifespan_engine)
    try:
        ConfigService(SystemConfigRepository(session)).seed_defaults()
    finally:
        session.close()
        startup_session.close()

    plugin_router = APIRouter(prefix="/api/plugins")
    for pr in plugin_manager.registry.api_routers:
        try:
            pr.register_routes(plugin_router)
        except Exception as e:
            logging.error(f"Error registering API routes for plugin: {e}")
    app.include_router(plugin_router)

    yield

    for lifecycle_hook in plugin_manager.registry.lifecycles:
        try:
            lifecycle_hook.on_shutdown()
        except Exception as e:
            logging.error(f"Error in plugin shutdown hook: {e}")

    plugin_manager.unload_all()


app = FastAPI(title="salus", lifespan=lifespan)
app.state.engine = engine
app.state.event_bus = InMemoryEventBus()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(i18n_middleware)

secure_endpoints = {"/docs", "/openapi.json", "/redoc"}


async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if request.url.path not in secure_endpoints and not request.url.path.startswith("/api/"):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob:; "
            "connect-src 'self'"
        )
    return response

app.middleware("http")(security_headers_middleware)

app.include_router(api_auth.router)
app.include_router(api_dashboard.router)
app.include_router(api_misc.router)
app.include_router(api_settings.router)
app.include_router(api_admin.router)
app.include_router(api_sharing.router)
app.include_router(api.router)
app.include_router(webhook.router)
app.include_router(export.router)
app.include_router(sharing.router)
app.include_router(workout.router)
app.include_router(asymmetric_share.router)
app.include_router(open_science.router)
app.include_router(api_sync.router)
api_dynamic.register_crud_routes(app)

frontend_build = os.path.join(
    os.path.dirname(__file__), "..", "..", "frontend", "build"
)
if os.path.isdir(frontend_build) and os.path.isfile(
    os.path.join(frontend_build, "index.html")
):
    app.mount("/", SPAStaticFiles(directory=frontend_build), name="frontend")


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"error": exc.message})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"error": exc.message})


@app.exception_handler(AuthenticationError)
async def auth_error_handler(request: Request, exc: AuthenticationError):
    return JSONResponse(status_code=401, content={"error": exc.message})


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError):
    return JSONResponse(status_code=403, content={"error": exc.message})


@app.exception_handler(404)
async def not_found_fallback(request: Request, exc: Exception):
    return JSONResponse(status_code=404, content={"error": "Not Found"})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.error(
        "Unhandled exception on %s %s:\n%s",
        request.method,
        request.url.path,
        "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
    )
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
