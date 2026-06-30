
class TestAdminPanel:
    def test_non_admin_redirected(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "bob",
                "password": "secret123",
                "email": "bob@example.com",
                "display_name": "Bob",
            },
            follow_redirects=True,
        )
        response = client.get("/admin", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"

    def test_admin_can_access(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        assert response.status_code == 200
        html = response.text
        assert "Admin Panel" in html

    def test_admin_page_shows_stats(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        assert response.status_code == 200
        html = response.text
        assert "System Statistics" in html
        assert "Total Users" in html
        assert "Total Measurements" in html
        assert "Metric Types" in html
        assert "Total Goals" in html

    def test_admin_page_shows_user_table(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "charlie",
                "password": "test1234",
                "email": "charlie@example.com",
                "display_name": "Charlie",
            },
            follow_redirects=True,
        )
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        assert response.status_code == 200
        html = response.text
        assert "admin" in html
        assert "charlie" in html
        assert "Users" in html

    def test_admin_nav_visible_for_admin(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        assert 'href="/admin"' in html
        assert "admin_panel_settings" in html

    def test_admin_nav_hidden_for_non_admin(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "dave",
                "password": "test1234",
                "email": "dave@example.com",
                "display_name": "Dave",
            },
            follow_redirects=True,
        )
        response = client.get("/")
        assert response.status_code == 200
        html = response.text
        assert 'href="/admin"' not in html


class TestAdminUserManagement:
    def test_toggle_admin(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "eve",
                "password": "test1234",
                "email": "eve@example.com",
                "display_name": "Eve",
            },
            follow_redirects=True,
        )
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )

        response = client.get("/admin")
        assert "Make Admin" in response.text

        response = client.post("/admin/users/2/toggle-admin")
        assert response.status_code == 200
        assert "Demote" in response.text

    def test_toggle_active(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "frank",
                "password": "test1234",
                "email": "frank@example.com",
                "display_name": "Frank",
            },
            follow_redirects=True,
        )
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )

        response = client.get("/admin")
        assert "Deactivate" in response.text

        response = client.post("/admin/users/2/toggle-active")
        assert response.status_code == 200
        assert "Activate" in response.text

    def test_non_admin_cannot_toggle_admin(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "grace",
                "password": "test1234",
                "email": "grace@example.com",
                "display_name": "Grace",
            },
            follow_redirects=True,
        )
        response = client.post("/admin/users/1/toggle-admin", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"

    def test_non_admin_cannot_toggle_active(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "heidi",
                "password": "test1234",
                "email": "heidi@example.com",
                "display_name": "Heidi",
            },
            follow_redirects=True,
        )
        response = client.post("/admin/users/1/toggle-active", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"


class TestAdminTokens:
    def test_token_overview_visible(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        assert response.status_code == 200
        assert "API Tokens" in response.text

    def test_revoke_token_as_admin(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "judy",
                "password": "test1234",
                "email": "judy@example.com",
                "display_name": "Judy",
            },
            follow_redirects=True,
        )
        client.post(
            "/settings/api-tokens",
            data={
                "label": "test-token",
                "scopes": "ingest:write",
            },
        )
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        assert "test-token" in response.text

        response = client.delete("/admin/tokens/1")
        assert response.status_code == 200
        assert "test-token" not in response.text

    def test_non_admin_cannot_revoke_token(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "karl",
                "password": "test1234",
                "email": "karl@example.com",
                "display_name": "Karl",
            },
            follow_redirects=True,
        )
        response = client.delete("/admin/tokens/1", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"


class TestAdminStatsAccuracy:
    def test_stats_reflect_data(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        client.post(
            "/auth/register",
            data={
                "username": "liam",
                "password": "test1234",
                "email": "liam@example.com",
                "display_name": "Liam",
            },
            follow_redirects=True,
        )
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        assert "Total Users" in response.text
        assert response.status_code == 200


class TestFirstUserAdmin:
    def test_first_registration_is_admin(self):
        from fastapi.testclient import TestClient
        from sqlalchemy.pool import StaticPool
        from sqlmodel import Session, SQLModel, create_engine

        from salus.database import get_session
        from salus.main import app, templates

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

        with TestClient(app) as c:
            resp = c.post(
                "/auth/register",
                data={
                    "username": "firstuser",
                    "password": "secret123",
                    "email": "first@example.com",
                    "display_name": "First",
                },
                follow_redirects=True,
            )
            assert resp.status_code == 200
            assert 'href="/admin"' in resp.text

        app.dependency_overrides.clear()

    def test_second_registration_is_not_admin(self):
        from fastapi.testclient import TestClient
        from sqlalchemy.pool import StaticPool
        from sqlmodel import Session, SQLModel, create_engine

        from salus.database import get_session
        from salus.main import app, templates

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

        with TestClient(app) as c:
            c.post(
                "/auth/register",
                data={
                    "username": "firstuser",
                    "password": "secret123",
                    "email": "first@example.com",
                    "display_name": "First",
                },
                follow_redirects=True,
            )
            c.post(
                "/auth/login",
                data={"username": "firstuser", "password": "secret123"},
                follow_redirects=True,
            )
            c.post("/auth/logout", follow_redirects=True)

            resp = c.post(
                "/auth/register",
                data={
                    "username": "seconduser",
                    "password": "secret123",
                    "email": "second@example.com",
                    "display_name": "Second",
                },
                follow_redirects=True,
            )
            assert resp.status_code == 200
            assert 'href="/admin"' not in resp.text

        app.dependency_overrides.clear()


class TestAdminUserDelete:
    def test_delete_user(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "deleteme",
                "password": "test1234",
                "email": "delete@example.com",
                "display_name": "Delete Me",
            },
            follow_redirects=True,
        )
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        assert "deleteme" in response.text

        response = client.delete("/admin/users/2")
        assert response.status_code == 200
        assert "deleteme" not in response.text

    def test_cannot_delete_self(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.delete("/admin/users/1")
        assert response.status_code == 409
        assert "Cannot delete your own account" in response.text

    def test_non_admin_cannot_delete(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "nonadmin",
                "password": "test1234",
                "email": "nonadmin@example.com",
                "display_name": "Non Admin",
            },
            follow_redirects=True,
        )
        response = client.delete("/admin/users/1", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"


class TestAdminUserDetail:
    def test_user_detail_loads(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin/users/1/detail")
        assert response.status_code == 200
        assert "admin" in response.text
        assert "admin@salus.local" in response.text

    def test_user_detail_requires_admin(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "regular",
                "password": "test1234",
                "email": "regular@example.com",
                "display_name": "Regular",
            },
            follow_redirects=True,
        )
        response = client.get("/admin/users/1/detail", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"


class TestAdminStorageStats:
    def test_storage_stats_visible(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        assert response.status_code == 200
        assert "Database Size" in response.text


class TestAdminConfig:
    def test_config_visible(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        assert response.status_code == 200
        assert "System Configuration" in response.text
        assert "general" in response.text.lower() or "security" in response.text.lower()

    def test_config_shows_security_category(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        assert response.status_code == 200
        assert "security" in response.text.lower()

    def test_config_edit_non_secret(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin/config/jwt_expire_minutes/edit")
        assert response.status_code == 200
        assert "1440" in response.text

    def test_config_update_value(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.put(
            "/admin/config/app_name",
            data={"value": "MySalus"},
        )
        assert response.status_code == 200
        assert "MySalus" in response.text

    def test_config_secret_masked(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin")
        html = response.text
        assert "••••••••" in html

    def test_config_reveal_secret(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/admin/config/jwt_secret_key/reveal")
        assert response.status_code == 200
        assert "change-me-in-production" in response.text

    def test_config_non_admin_cannot_access(self, client):
        client.post(
            "/auth/register",
            data={
                "username": "normie",
                "password": "test1234",
                "email": "normie@example.com",
                "display_name": "Normie",
            },
            follow_redirects=True,
        )
        response = client.get("/admin/config/security", follow_redirects=False)
        assert response.status_code == 303
        assert response.headers["location"] == "/"


class TestTheme:
    def test_default_theme_is_system(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.get("/settings")
        assert response.status_code == 200
        assert 'value="system"' in response.text
        assert "checked" in response.text
        assert 'data-theme="system"' in response.text

    def test_set_theme_to_dark(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.post(
            "/settings/theme",
            data={"theme": "dark"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert 'value="dark"' in response.text
        assert "checked" in response.text
        assert 'data-theme="dark"' in response.text

    def test_set_theme_to_light(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        response = client.post(
            "/settings/theme",
            data={"theme": "light"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert 'value="light"' in response.text
        assert "checked" in response.text
        assert 'data-theme="light"' in response.text

    def test_theme_persists_across_requests(self, client):
        client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin"},
            follow_redirects=True,
        )
        client.post(
            "/settings/theme",
            data={"theme": "dark"},
            follow_redirects=True,
        )
        response = client.get("/")
        assert 'data-theme="dark"' in response.text

    def test_theme_requires_auth(self, client):
        response = client.post("/settings/theme", data={"theme": "dark"}, follow_redirects=False)
        assert response.status_code == 303
        assert "/auth/login" in response.headers["location"]
