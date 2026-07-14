def _login_as_admin(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "admin"},
    )
    token = resp.json()["token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return token
def _get_admin_id(client):
    users = client.get("/api/v1/admin/users").json()
    admin = next(u for u in users if u["username"] == "admin")
    return admin["id"]

def _register(client, username, password="test1234", email=None, display_name=None):
    resp = client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": password,
            "email": email or f"{username}@example.com",
            "display_name": display_name or username.capitalize(),
        },
    )
    return resp.json()["token"]


def test_admin_non_admin_rejected(client):
    token = _register(client, "bob")
    client.headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/admin/stats")
    assert response.status_code in (401, 403)


def test_admin_can_access_stats(client):
    _login_as_admin(client)
    response = client.get("/api/v1/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "storage" in data
    assert "total_users" in data["stats"]


def test_admin_can_list_users(client):
    _login_as_admin(client)
    _register(client, "charlie")

    _login_as_admin(client)
    response = client.get("/api/v1/admin/users")
    assert response.status_code == 200
    data = response.json()
    usernames = [u["username"] for u in data]
    assert "admin" in usernames
    assert "charlie" in usernames


def test_admin_toggle_admin(client):
    _register(client, "eve")
    _login_as_admin(client)

    users = client.get("/api/v1/admin/users").json()
    eve = next(u for u in users if u["username"] == "eve")
    assert eve["is_admin"] is False

    response = client.post(f"/api/v1/admin/users/{eve['id']}/toggle-admin")
    assert response.status_code == 204

    users = client.get("/api/v1/admin/users").json()
    eve = next(u for u in users if u["username"] == "eve")
    assert eve["is_admin"] is True


def test_admin_toggle_active(client):
    _register(client, "frank")
    _login_as_admin(client)

    users = client.get("/api/v1/admin/users").json()
    frank = next(u for u in users if u["username"] == "frank")
    assert frank["is_active"] is True

    response = client.post(f"/api/v1/admin/users/{frank['id']}/toggle-active")
    assert response.status_code == 204

    users = client.get("/api/v1/admin/users").json()
    frank = next(u for u in users if u["username"] == "frank")
    assert frank["is_active"] is False


def test_non_admin_cannot_toggle_admin(client):
    token = _register(client, "grace")
    client.headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/admin/users/1/toggle-admin")
    assert response.status_code in (401, 403)


def test_non_admin_cannot_toggle_active(client):
    token = _register(client, "heidi")
    client.headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/admin/users/1/toggle-active")
    assert response.status_code in (401, 403)


def test_admin_delete_user(client):
    _register(client, "deleteme")
    _login_as_admin(client)

    users = client.get("/api/v1/admin/users").json()
    deleteme = next(u for u in users if u["username"] == "deleteme")

    response = client.delete(f"/api/v1/admin/users/{deleteme['id']}")
    assert response.status_code == 204

    users = client.get("/api/v1/admin/users").json()
    assert "deleteme" not in [u["username"] for u in users]


def test_cannot_delete_self(client):
    _login_as_admin(client)
    admin_id = _get_admin_id(client)
    response = client.delete(f"/api/v1/admin/users/{admin_id}")
    assert response.status_code == 409
    assert "Cannot delete your own account" in response.json()["error"]


def test_non_admin_cannot_delete(client):
    token = _register(client, "nonadmin")
    client.headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/api/v1/admin/users/1")  # Any invalid or arbitrary ID since non-admin gets rejected anyway
    assert response.status_code in (401, 403)


def test_admin_user_detail(client):
    _login_as_admin(client)
    admin_id = _get_admin_id(client)
    response = client.get(f"/api/v1/admin/users/{admin_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"


def test_user_detail_requires_admin(client):
    token = _register(client, "regular")
    client.headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/admin/users/1")
    assert response.status_code in (401, 403)


def test_admin_config_list(client):
    _login_as_admin(client)
    response = client.get("/api/v1/admin/config")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_admin_config_update(client):
    _login_as_admin(client)
    response = client.put(
        "/api/v1/admin/config/app_name",
        json={"value": "MySalus"},
    )
    assert response.status_code == 200
    assert response.json()["value"] == "MySalus"


def test_admin_config_non_admin_cannot_access(client):
    token = _register(client, "normie")
    client.headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/admin/config")
    assert response.status_code in (401, 403)


class TestFirstUserAdmin:
    def test_first_registration_is_admin(self):
        from fastapi.testclient import TestClient
        from sqlalchemy.pool import StaticPool
        from sqlmodel import Session, SQLModel, create_engine

        from salus.database import get_session
        from salus.main import app

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
        app.state.engine = engine

        with TestClient(app) as c:
            resp = c.post(
                "/api/v1/auth/register",
                json={
                    "username": "firstuser",
                    "password": "secret123",
                    "email": "first@example.com",
                    "display_name": "First",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["user"]["is_admin"] is True

        app.dependency_overrides.clear()
        del app.state.engine

    def test_second_registration_is_not_admin(self):
        from fastapi.testclient import TestClient
        from sqlalchemy.pool import StaticPool
        from sqlmodel import Session, SQLModel, create_engine

        from salus.database import get_session
        from salus.main import app

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
        app.state.engine = engine

        with TestClient(app) as c:
            c.post(
                "/api/v1/auth/register",
                json={
                    "username": "firstuser",
                    "password": "secret123",
                    "email": "first@example.com",
                    "display_name": "First",
                },
            )
            resp = c.post(
                "/api/v1/auth/register",
                json={
                    "username": "seconduser",
                    "password": "secret123",
                    "email": "second@example.com",
                    "display_name": "Second",
                },
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["user"]["is_admin"] is False

        app.dependency_overrides.clear()
        del app.state.engine
