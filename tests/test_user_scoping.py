def test_user_data_scoped(authenticated_client, client):
    authenticated_client.post(
        "/api/v1/metrics",
        json={"name": "AliceCustom", "unit": "kg", "data_type": "number", "color": "#ef4444"},
    )
    authenticated_client.post(
        "/api/v1/entries?metric_type_id=1",
        json={"value": "80.5"},
    )

    client.post("/api/v1/auth/logout")
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "bob", "password": "secret456"},
    )
    bob_token = resp.json()["token"]
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    response = client.get("/api/v1/metrics", headers=bob_headers)
    assert response.status_code == 200
    metrics = response.json()
    names = [m["name"] for m in metrics]
    assert "AliceCustom" not in names

    response = client.get("/api/v1/entries?metric_type_id=1", headers=bob_headers)
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_alice_cannot_see_bob_metrics(authenticated_client, client):
    client.post("/api/v1/auth/logout")
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": "bob", "password": "secret456"},
    )
    bob_token = resp.json()["token"]

    client.post(
        "/api/v1/metrics",
        json={"name": "Hydration", "unit": "ml", "data_type": "number", "color": "#0ea5e9"},
        headers={"Authorization": f"Bearer {bob_token}"},
    )

    response = authenticated_client.get("/api/v1/metrics")
    names = [m["name"] for m in response.json()]
    assert "Hydration" not in names


def test_settings_page_loads(authenticated_client):
    response = authenticated_client.get("/api/v1/settings/account")
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["username"] == "alice"
    assert "identities" in data
    assert "api_tokens" in data


def test_change_password(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/settings/password",
        json={"current_password": "secret123", "new_password": "newpass789"},
    )
    assert response.status_code == 200
    assert "Password changed" in response.json()["message"]

