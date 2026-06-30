import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel

from salus.config import settings as app_settings
from salus.database import engine
from salus.exceptions import AuthenticationError, ConflictError, NotFoundError
from salus.routers import analytics, api, auth, dashboard, entries, export, goals, metrics, onboarding, settings, webhook

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

templates = Jinja2Templates(directory="src/salus/templates")
templates.env.globals["settings"] = app_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    app.state.templates = templates
    yield


app = FastAPI(title="salus", lifespan=lifespan)
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


@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> HTMLResponse:
    return HTMLResponse(status_code=404, content=exc.message)


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> HTMLResponse:
    return HTMLResponse(status_code=409, content=exc.message)


@app.exception_handler(AuthenticationError)
async def auth_error_handler(request: Request, exc: AuthenticationError) -> RedirectResponse:
    return RedirectResponse(url="/auth/login", status_code=303)


@app.exception_handler(404)
async def not_found_fallback(request: Request, exc: Exception) -> RedirectResponse:
    return RedirectResponse(url="/", status_code=303)
