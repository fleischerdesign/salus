import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from salus.database import get_session
from salus.main import app, templates
from salus.models.user import User
from salus.services.password import hash_password


def _seed_admin(session: Session) -> None:
    admin = User(
        username="admin",
        password_hash=hash_password("admin"),
        email="admin@salus.local",
        display_name="Admin",
        is_admin=True,
    )
    session.add(admin)
    session.commit()


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        return Session(engine)

    app.dependency_overrides[get_session] = override_get_session
    app.state.templates = templates

    _seed_admin(Session(engine))

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(client):
    """Registered + logged-in user."""
    client.post(
        "/auth/register",
        data={
            "username": "alice",
            "password": "secret123",
            "email": "alice@example.com",
            "display_name": "Alice",
        },
        follow_redirects=True,
    )
    return client
