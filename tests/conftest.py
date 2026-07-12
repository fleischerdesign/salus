import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from salus.database import get_session
from salus.main import app
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

    # Seed default metric types for the admin user to enable correct webhook mapping
    from salus.services.metric_type_mapping import DEFAULT_METRIC_TYPES
    from salus.models import MetricType
    for name, unit, data_type, color, source_data_type, icon, widget_size, widget_enabled in DEFAULT_METRIC_TYPES:
        mt = MetricType(
            name=name,
            unit=unit,
            data_type=data_type,
            color=color,
            user_id=admin.id,
            is_system=True,
            source_data_type=source_data_type,
            icon=icon,
            widget_size=widget_size,
            widget_enabled=widget_enabled,
        )
        session.add(mt)
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
