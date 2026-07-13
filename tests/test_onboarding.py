def test_dismiss_onboarding(authenticated_client):
    response = authenticated_client.post("/api/v1/onboarding/dismiss")
    assert response.status_code == 204


def test_onboarding_create_token_endpoint(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/onboarding/token?label=Test Token&scopes=ingest:write",
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "webhook_url" in data


def test_onboarding_create_entry_endpoint(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/onboarding/entry",
        json={"metric_type_id": 1, "value": "42"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == "42"
    assert data["metric_type_id"] == 1


def test_onboarding_create_goal_endpoint(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/onboarding/goal",
        json={"metric_type_id": 1, "target_value": 100, "direction": "increase"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["metric_type_id"] == 1
    assert data["target_value"] == 100


def test_onboarding_requires_auth(client):
    response = client.post("/api/v1/onboarding/dismiss", follow_redirects=False)
    assert response.status_code in (401, 403)


def test_onboarding_token_requires_auth(client):
    response = client.post("/api/v1/onboarding/token?label=X", follow_redirects=False)
    assert response.status_code in (401, 403)


def test_onboarding_entry_requires_auth(client):
    response = client.post(
        "/api/v1/onboarding/entry",
        json={"metric_type_id": 1, "value": "1"},
        follow_redirects=False,
    )
    assert response.status_code in (401, 403)


def test_onboarding_goal_requires_auth(client):
    response = client.post(
        "/api/v1/onboarding/goal",
        json={"metric_type_id": 1, "target_value": 1},
        follow_redirects=False,
    )
    assert response.status_code in (401, 403)
