def test_dynamic_api_unauthenticated(client):
    response = client.get("/api/v1/metric_type", follow_redirects=False)
    assert response.status_code in (401, 403)


def test_dynamic_api_list_metric_types(authenticated_client):
    response = authenticated_client.get("/api/v1/metric_type")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    names = [m["name"] for m in data]
    assert "Steps" in names
    assert "Heart Rate" in names


def test_dynamic_api_get_metric_type_detail(authenticated_client):
    response = authenticated_client.get("/api/v1/metric_type")
    data = response.json()
    assert len(data) > 0
    first = data[0]
    first_id = first["id"]

    detail = authenticated_client.get(f"/api/v1/metric_type/{first_id}")
    assert detail.status_code == 200
    assert detail.json()["name"] == first["name"]
    assert detail.json()["id"] == first_id


def test_dynamic_api_get_nonexistent_returns_404(authenticated_client):
    response = authenticated_client.get("/api/v1/metric_type/99999")
    assert response.status_code == 404


def test_dynamic_api_pagination(authenticated_client):
    response = authenticated_client.get("/api/v1/metric_type?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2


def test_dynamic_api_list_goals(authenticated_client):
    response = authenticated_client.get("/api/v1/goal")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_dynamic_api_create_and_list_goal(authenticated_client):
    metrics = authenticated_client.get("/api/v1/metric_type").json()
    steps = next(m for m in metrics if m["name"] == "Steps")

    create_resp = authenticated_client.post(
        "/api/v1/goal",
        json={
            "metric_type_id": steps["id"],
            "target_value": 8000,
            "direction": "increase",
            "frequency": "daily",
        },
    )
    assert create_resp.status_code == 200
    goal_id = create_resp.json()["id"]

    detail = authenticated_client.get(f"/api/v1/goal/{goal_id}")
    assert detail.status_code == 200
    assert detail.json()["target_value"] == 8000


def test_dynamic_api_user_isolation(authenticated_client, client):
    """Verify user A's entities are not visible to user B."""
    import random
    suffix = random.randint(10000, 99999)
    authenticated_client.post(
        "/api/v1/metric_type",
        json={"name": f"PrivateMetric_{suffix}", "unit": "x", "data_type": "number", "color": "#000"},
    )

    # Register user B
    register_data = {"username": f"other_{suffix}", "password": "secret"}
    client.post("/api/v1/auth/register", json=register_data)
    login_resp = client.post("/api/v1/auth/login", json=register_data)
    token_b = login_resp.json()["token"]

    response = client.get(
        "/api/v1/metric_type",
        headers={"Authorization": f"Bearer {token_b}"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    names = [m["name"] for m in response.json()]
    assert f"PrivateMetric_{suffix}" not in names
    assert "Steps" in names


def test_dynamic_api_soft_delete_hides_record(authenticated_client):
    """Soft-deleted records are excluded from GET list and detail."""
    metrics = authenticated_client.get("/api/v1/metric_type").json()
    steps = next(m for m in metrics if m["name"] == "Steps")

    resp = authenticated_client.post(
        "/api/v1/goal",
        json={
            "metric_type_id": steps["id"],
            "target_value": 5000,
            "direction": "increase",
            "frequency": "daily",
        },
    )
    assert resp.status_code == 200
    goal_id = resp.json()["id"]

    del_resp = authenticated_client.delete(f"/api/v1/goal/{goal_id}")
    assert del_resp.status_code == 204

    detail = authenticated_client.get(f"/api/v1/goal/{goal_id}")
    assert detail.status_code == 404
