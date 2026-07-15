def test_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "password": "secret123",
            "email": "test@example.com",
            "display_name": "Test User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["user"]["username"] == "testuser"
    assert data["user"]["email"] == "test@example.com"


def test_register_duplicate_username(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "dup", "password": "secret123"},
    )
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "dup", "password": "other456"},
    )
    assert response.status_code == 409
    assert "already taken" in response.json()["error"]


def test_register_duplicate_email(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "user1",
            "password": "secret123",
            "email": "same@example.com",
        },
    )
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "user2",
            "password": "other456",
            "email": "same@example.com",
        },
    )
    assert response.status_code == 409
    assert "already registered" in response.json()["error"]


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={"username": "loginuser", "password": "secret123"},
    )
    client.post("/api/v1/auth/logout")

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "loginuser", "password": "secret123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "salus_session" in response.cookies


def test_login_invalid_credentials(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nobody", "password": "wrong"},
    )
    assert response.status_code == 401
    assert "Invalid" in response.json()["error"]["message"]


def test_logout_clears_cookie(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "logoutuser", "password": "secret123"},
    )
    assert "salus_session" in resp.cookies

    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 204
    assert "salus_session" not in response.cookies or response.cookies.get("salus_session", "") == ""


def test_auth_me_returns_profile(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "meuser", "password": "secret123"},
    )
    token = resp.json()["token"]

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "meuser"
    assert "is_admin" in data


def test_auth_me_rejects_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
