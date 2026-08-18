import logging
import os
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from salus.config import DEFAULT_API_TOKEN, DEFAULT_JWT_SECRET_KEY, settings
from salus.database import Session, engine
from salus.dependencies import limiter
from salus.exceptions import (
    ApiError,
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
    api_achievement,
    api_admin,
    api_analytics,
    api_auth,
    api_dashboard,
    api_food,
    api_habit,
    api_journal,
    api_meal,
    api_medication,
    api_misc,
    api_mood,
    api_recipe,
    api_rest,
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
from salus.services.background_ingestion import BackgroundIngestionService
from salus.services.parser import FlexiblePayloadParser
from salus.services.sharing import SharingService
from salus.services.webhook_ingestion import WebhookIngestionService
from salus.services.achievement.service import AchievementService
from salus.services.metric_definition import MetricDefinitionService
from salus.services.mood import MoodService
from salus.services.lab import LabService
from salus.services.food_item import FoodItemService
from salus.services.exercise import ExerciseService
from salus.services.scheduler import AppScheduler
from salus.services.data_quality import (
    DataQualityCleanupJob,
    DataQualityRecheckJob,
    register_write_hooks,
)


def _check_secrets() -> None:
    if settings.is_production:
        if settings.jwt_secret_key == DEFAULT_JWT_SECRET_KEY:
            raise RuntimeError("SALUS_JWT_SECRET_KEY is set to the default value — set a strong random key for production.")
        if settings.api_token == DEFAULT_API_TOKEN:
            raise RuntimeError("SALUS_API_TOKEN is set to the default value — set a unique token for production.")
        return

    warned = False
    if settings.jwt_secret_key == DEFAULT_JWT_SECRET_KEY:
        logging.warning("SALUS_JWT_SECRET_KEY is set to the default value — generate a strong random key for production.")
        warned = True
    if settings.api_token == DEFAULT_API_TOKEN:
        logging.warning("SALUS_API_TOKEN is set to the default value — generate a unique token for production.")
        warned = True
    if warned:
        logging.warning("Default secrets detected. Set SALUS_JWT_SECRET_KEY and SALUS_API_TOKEN env vars for production use.")


class SPAStaticFiles(StaticFiles):
    """Serves SvelteKit SPA build with fallback to index.html for client-side routing."""

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code == 404 and not path.startswith(("api/", "webhook/", ".well-known/")) and not path.endswith((".js", ".css", ".png", ".svg", ".woff2", ".ico", ".json")):
                return await super().get_response("index.html", scope)
            raise


def _run_seeder(label: str, seed_fn, *, fatal: bool = False) -> None:
    try:
        seed_fn()
    except Exception:
        logging.error(f"Failed to seed {label}", exc_info=True)
        if fatal:
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    _check_secrets()

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

    def _build_webhook_service(session: Session) -> WebhookIngestionService:
        from salus.repositories.measurement import MeasurementRepository
        from salus.repositories.metric_definition import MetricDefinitionRepository
        from salus.services.metric_type_mapping import MetricDefinitionMappingService

        return WebhookIngestionService(
            FlexiblePayloadParser(),
            MeasurementRepository(session),
            MetricDefinitionMappingService(MetricDefinitionRepository(session)),
        )

    def _build_sharing_service(uow) -> SharingService:
        return SharingService.create(uow)

    app.state.background_ingestion = BackgroundIngestionService(
        lambda: Session(lifespan_engine),
        lambda: FlexiblePayloadParser(),
        _build_webhook_service,
        _build_sharing_service,
    )

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

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    alembic_ini_path = os.path.join(base_dir, "alembic.ini")
    if not os.path.exists(alembic_ini_path):
        alembic_ini_path = "alembic.ini"

    if os.path.exists(alembic_ini_path):
        alembic_cfg = Config(alembic_ini_path)
    else:
        alembic_cfg = Config()

    migrations_dir = os.path.join(base_dir, "migrations")
    if os.path.isdir(migrations_dir):
        alembic_cfg.set_main_option("script_location", migrations_dir)
    elif not alembic_cfg.get_main_option("script_location"):
        alembic_cfg.set_main_option("script_location", "migrations")

    inspector = inspect(lifespan_engine)
    with lifespan_engine.connect() as connection:
        alembic_cfg.attributes["connection"] = connection
        if (
            "user" in inspector.get_table_names()
            and "alembic_version" not in inspector.get_table_names()
        ):
            command.stamp(alembic_cfg, "head")
        else:
            try:
                command.upgrade(alembic_cfg, "head")
            except Exception as e:
                logging.warning(f"Alembic upgrade warning: {e}")

    from sqlmodel import SQLModel
    import salus.models  # noqa: F401
    SQLModel.metadata.create_all(lifespan_engine)

    session = Session(lifespan_engine)
    try:
        _run_seeder(
            "default config",
            lambda: ConfigService(SystemConfigRepository(session)).seed_defaults(),
            fatal=True,
        )
        _run_seeder(
            "metric definitions",
            lambda: MetricDefinitionService(uow).seed_definitions(),
        )
        _run_seeder(
            "achievement definitions",
            lambda: AchievementService(uow).seed_definitions(),
        )
        _run_seeder("mood tags", lambda: MoodService(uow).seed_tags())
        _run_seeder("lab markers", lambda: LabService(uow).seed_markers())
        _run_seeder("common foods", lambda: FoodItemService(uow).seed_common_foods())
        _run_seeder("common exercises", lambda: ExerciseService(uow).seed_common_exercises())
        startup_session.commit()
    finally:
        session.close()
        startup_session.close()

    scheduler = AppScheduler(lambda: Session(lifespan_engine))
    scheduler.add(DataQualityRecheckJob(interval_seconds=settings.data_quality_recheck_interval_hours * 3600))
    scheduler.add(DataQualityCleanupJob(interval_seconds=settings.data_quality_cleanup_interval_hours * 3600))
    await scheduler.start()
    app.state.scheduler = scheduler

    plugin_router = APIRouter(prefix="/api/plugins")
    for pr in plugin_manager.registry.api_routers:
        try:
            pr.register_routes(plugin_router)
        except Exception as e:
            logging.error(f"Error registering API routes for plugin: {e}")
    app.include_router(plugin_router)

    yield

    await scheduler.stop()

    for lifecycle_hook in plugin_manager.registry.lifecycles:
        try:
            lifecycle_hook.on_shutdown()
        except Exception as e:
            logging.error(f"Error in plugin shutdown hook: {e}")

    plugin_manager.unload_all()


def create_app() -> FastAPI:
    register_write_hooks()
    app = FastAPI(title="salus", lifespan=lifespan)
    app.state.engine = engine
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # pyright: ignore[reportArgumentType]
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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
                "font-src 'self' data: https://fonts.gstatic.com https://fonts.googleapis.com; "
                "img-src 'self' data: blob:; "
                "connect-src 'self'"
            )
        return response

    app.middleware("http")(security_headers_middleware)

    app.include_router(api_auth.router)
    app.include_router(api_analytics.router)
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
    app.include_router(api_habit.router)
    app.include_router(api_mood.router)
    app.include_router(api_journal.router)
    app.include_router(api_achievement.router)
    app.include_router(api_medication.router)
    app.include_router(api_food.router)
    app.include_router(api_meal.router)
    app.include_router(api_recipe.router)
    api_rest.register_auto_crud(app)

    frontend_build = os.path.join(
        os.path.dirname(__file__), "..", "..", "frontend", "build"
    )
    if os.path.isdir(frontend_build) and os.path.isfile(
        os.path.join(frontend_build, "index.html")
    ):
        app.mount("/", SPAStaticFiles(directory=frontend_build), name="frontend")

    return app


app = create_app()


@app.exception_handler(ApiError)
async def api_error_handler(request: Request, exc: ApiError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


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
