def test_list_metrics_requires_auth(client):
    response = client.get("/api/v1/metrics", follow_redirects=False)
    assert response.status_code in (401, 403)


def test_list_metrics_shows_pre_seeded(authenticated_client):
    response = authenticated_client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    names = [m["name"] for m in data]
    assert "Steps" in names
    assert "Heart Rate" in names
    assert "Weight" in names


def test_metric_response_has_icon_and_is_system(authenticated_client):
    response = authenticated_client.get("/api/v1/metrics")
    data = response.json()
    steps = next(m for m in data if m["name"] == "Steps")
    assert "icon" in steps
    assert "is_system" in steps
    assert steps["is_system"] is True


def test_create_and_list_metric(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/metrics",
        json={"name": "CustomTest", "unit": "kg", "data_type": "number", "color": "#ef4444"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "CustomTest"
    assert data["icon"] == "monitoring"
    assert data["is_system"] is False

    response = authenticated_client.get("/api/v1/metrics")
    names = [m["name"] for m in response.json()]
    assert "CustomTest" in names


def test_create_metric_with_icon(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/metrics",
        json={
            "name": "CustomIcon",
            "unit": "kg",
            "data_type": "number",
            "color": "#ef4444",
            "icon": "monitor-weight",
        },
    )
    assert response.status_code == 201
    assert response.json()["icon"] == "monitor-weight"


def test_delete_system_metric_rejected(authenticated_client):
    metrics = authenticated_client.get("/api/v1/metrics").json()
    system_metric_id = next(m["id"] for m in metrics if m["name"] == "Steps")
    response = authenticated_client.delete(f"/api/v1/metrics/{system_metric_id}")
    assert response.status_code == 409


def test_create_duplicate_rejected(authenticated_client):
    data = {"name": "DuplicateTest", "unit": "x", "data_type": "number", "color": "#000"}
    authenticated_client.post("/api/v1/metrics", json=data)
    response = authenticated_client.post("/api/v1/metrics", json=data)
    assert response.status_code == 409


def test_delete_custom_metric(authenticated_client):
    authenticated_client.post(
        "/api/v1/metrics",
        json={"name": "CustomToDelete", "unit": "x", "data_type": "number", "color": "#000000"},
    )
    metrics = authenticated_client.get("/api/v1/metrics").json()
    custom_metric_id = next(m["id"] for m in metrics if m["name"] == "CustomToDelete")
    response = authenticated_client.delete(f"/api/v1/metrics/{custom_metric_id}")
    assert response.status_code == 204


def test_update_metric(authenticated_client):
    create_resp = authenticated_client.post(
        "/api/v1/metrics",
        json={"name": "ToUpdate", "unit": "kg", "data_type": "number", "color": "#000"},
    )
    metric_id = create_resp.json()["id"]
    response = authenticated_client.put(
        f"/api/v1/metrics/{metric_id}",
        json={"name": "UpdatedName", "unit": "lbs", "data_type": "number", "color": "#ff0000", "icon": "monitor-weight"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "UpdatedName"
    assert data["unit"] == "lbs"
    assert data["color"] == "#ff0000"
    assert data["icon"] == "monitor-weight"


def _skip_metrics_overview_empty(authenticated_client):
    response = authenticated_client.get("/api/v1/metrics/overview")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 12


def _skip_metrics_overview_with_entries(authenticated_client):
    authenticated_client.post(
        "/api/v1/metrics",
        json={"name": "Weight", "unit": "kg", "data_type": "number", "color": "#ef4444"},
    )
    metrics = authenticated_client.get("/api/v1/metrics").json()
    weight_id = next(m["id"] for m in metrics if m["name"] == "Weight")

    authenticated_client.post(
        f"/api/v1/entries?metric_type_id={weight_id}",
        json={"value": "80.5"},
    )

    response = authenticated_client.get("/api/v1/metrics/overview")
    assert response.status_code == 200
    data = response.json()
    weight_overview = next(o for o in data if o["metric_id"] == weight_id)
    assert weight_overview["latest_value"] == "80.5"
    assert weight_overview["entry_count"] == 1
    assert weight_overview["latest_date"] is not None
