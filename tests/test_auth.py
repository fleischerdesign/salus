def test_register_success(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "testuser",
            "password": "secret123",
            "email": "test@example.com",
            "display_name": "Test User",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "salus" in response.text


def test_register_duplicate_username(client):
    client.post(
        "/auth/register",
        data={"username": "dup", "password": "secret123"},
        follow_redirects=True,
    )
    response = client.post(
        "/auth/register",
        data={"username": "dup", "password": "other456"},
    )
    assert response.status_code == 409
    assert "already taken" in response.text


def test_register_duplicate_email(client):
    client.post(
        "/auth/register",
        data={
            "username": "user1",
            "password": "secret123",
            "email": "same@example.com",
        },
        follow_redirects=True,
    )
    response = client.post(
        "/auth/register",
        data={
            "username": "user2",
            "password": "other456",
            "email": "same@example.com",
        },
    )
    assert response.status_code == 409
    assert "already registered" in response.text


def test_login_success(client):
    client.post(
        "/auth/register",
        data={"username": "loginuser", "password": "secret123"},
        follow_redirects=True,
    )
    client.post("/auth/logout", follow_redirects=True)

    response = client.post(
        "/auth/login",
        data={"username": "loginuser", "password": "secret123"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "salus_session" in response.cookies


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        data={"username": "nobody", "password": "wrong"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "Invalid username" in response.text


def test_login_redirects_if_already_authenticated(authenticated_client):
    response = authenticated_client.get("/auth/login", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_register_page_redirects_if_authenticated(authenticated_client):
    response = authenticated_client.get("/auth/register", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_logout_clears_cookie(client):
    client.post(
        "/auth/register",
        data={"username": "logoutuser", "password": "secret123"},
        follow_redirects=True,
    )
    response = client.post("/auth/logout", follow_redirects=False)
    assert response.status_code == 303

    response = client.get("/entries", follow_redirects=False)
    assert response.status_code == 303


def test_login_page_loads(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert "Sign In" in response.text


def test_register_page_loads(client):
    response = client.get("/auth/register")
    assert response.status_code == 200
    assert "Create Account" in response.text
