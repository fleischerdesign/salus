import os

import pytest
from fastapi.testclient import TestClient
from slowapi import Limiter
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from salus.database import get_session
from salus.dependencies import limiter
from salus.main import app

limiter.enabled = False
from salus.models.user import User
from salus.repositories.system_config import SystemConfigRepository
from salus.services.config import ConfigService
from salus.services.password import hash_password

TEST_ADMIN_USER = "admin"
TEST_ADMIN_PASS = "admin"
TEST_USER_PASS = "secret123"
TEST_USERNAME = "alice"


def _seed_admin(session: Session) -> None:
    admin = User(
        username=TEST_ADMIN_USER,
        password_hash=hash_password(TEST_ADMIN_PASS),
        email="admin@salus.local",
        display_name="Admin",
        is_admin=True,
    )
    session.add(admin)
    session.commit()

    # Seed global metric definitions + groups + user preferences
    from salus.models.metric_definition import MetricDefinition, MetricGroup
    from salus.models.metric_preference import UserMetricPreference
    from salus.services.metric_type_mapping import METRIC_DEFINITIONS, METRIC_GROUPS, DEFAULT_METRIC_PREFERENCES

    for group_data in METRIC_GROUPS:
        session.add(MetricGroup(key=group_data["key"], name=group_data["name"], icon=group_data["icon"]))

    for md_data in METRIC_DEFINITIONS:
        session.add(MetricDefinition(**md_data))

    for p in DEFAULT_METRIC_PREFERENCES:
        session.add(UserMetricPreference(
            user_id=admin.id,
            metric_code=p["code"],
            enabled=p.get("enabled", True),
            color=p.get("color", "#4f46e5"),
            icon=p.get("icon", "monitoring"),
            widget_size=p.get("widget_size", "medium"),
            widget_enabled=p.get("widget_enabled", False),
            position=p.get("position", 0),
        ))

    session.commit()


@pytest.fixture
def client():
    db_url = os.environ.get("SALUS_TEST_DATABASE_URL", "sqlite://")
    if db_url.startswith("sqlite"):
        engine = create_engine(
            db_url,
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(db_url, echo=False)

    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    app.state.engine = engine

    _seed_admin(Session(engine))

    session = Session(engine)
    try:
        ConfigService(SystemConfigRepository(session)).seed_defaults()
    finally:
        session.close()

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    if hasattr(app.state, "engine"):
        del app.state.engine


@pytest.fixture
def db_engine():
    db_url = os.environ.get("SALUS_TEST_DATABASE_URL", "sqlite://")
    if db_url.startswith("sqlite"):
        engine = create_engine(
            db_url,
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        engine = create_engine(db_url, echo=False)
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def db_session(db_engine):
    with Session(db_engine) as session:
        yield session


@pytest.fixture
def session(db_engine):
    with Session(db_engine) as session:
        yield session


@pytest.fixture
def authenticated_client(client):
    """Registered + logged-in user via JSON API, stores JWT for Bearer auth."""
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": TEST_USERNAME,
            "password": TEST_USER_PASS,
            "email": "alice@example.com",
            "display_name": "Alice",
        },
    )
    data = resp.json()
    token = data.get("token", "")
    client.headers = {"Authorization": f"Bearer {token}"}
    return client
