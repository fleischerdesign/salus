def test_user_data_scoped(authenticated_client, client):
    """Alice creates metrics & entries. Bob logs in and sees none of them."""
    authenticated_client.post(
        "/metrics",
        data={"name": "Weight", "unit": "kg", "data_type": "number", "color": "#ef4444"},
        follow_redirects=True,
    )
    authenticated_client.post(
        "/entries",
        data={"value": "80.5", "metric_type_id": "1"},
        follow_redirects=True,
    )

    client.post("/auth/logout", follow_redirects=True)
    client.post(
        "/auth/register",
        data={"username": "bob", "password": "secret456"},
        follow_redirects=True,
    )

    response = client.get("/metrics")
    assert response.status_code == 200
    assert "Weight" not in response.text

    response = client.get("/")
    assert response.status_code == 200
    assert "80.5" not in response.text


def test_alice_cannot_see_bob_metrics(authenticated_client, client):
    """Bob creates metrics, Alice cannot see them."""
    client.post("/auth/logout", follow_redirects=True)
    client.post(
        "/auth/register",
        data={"username": "bob", "password": "secret456"},
        follow_redirects=True,
    )
    client.post(
        "/metrics",
        data={"name": "Hydration", "unit": "ml", "data_type": "number", "color": "#0ea5e9"},
        follow_redirects=True,
    )

    authenticated_client.post("/auth/logout", follow_redirects=True)
    authenticated_client.post(
        "/auth/login",
        data={"username": "alice", "password": "secret123"},
        follow_redirects=True,
    )

    response = authenticated_client.get("/metrics")
    assert "Hydration" not in response.text


def test_settings_page_loads(authenticated_client):
    response = authenticated_client.get("/settings")
    assert response.status_code == 200
    assert "Account Settings" in response.text


def test_change_password(authenticated_client):
    response = authenticated_client.post(
        "/settings/change-password",
        data={"current_password": "secret123", "new_password": "newpass789"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Password changed" in response.text
