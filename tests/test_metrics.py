def test_list_metrics_requires_auth(client):
    response = client.get("/metrics", follow_redirects=False)
    assert response.status_code == 303


def test_list_metrics_shows_pre_seeded(authenticated_client):
    response = authenticated_client.get("/metrics")
    assert response.status_code == 200
    assert "Steps" in response.text
    assert "Heart Rate" in response.text
    assert "Weight" in response.text


def test_create_and_list_metric(authenticated_client):
    response = authenticated_client.post(
        "/metrics",
        data={"name": "CustomTest", "unit": "kg", "data_type": "number", "color": "#ef4444"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = authenticated_client.get("/metrics")
    assert "CustomTest" in response.text


def test_delete_system_metric_rejected(authenticated_client):
    metrics = authenticated_client.get("/api/v1/metrics").json()
    system_metric_id = next(m["id"] for m in metrics if m["name"] == "Steps")
    response = authenticated_client.delete(f"/metrics/{system_metric_id}")
    assert response.status_code == 409


def test_create_duplicate_rejected(authenticated_client):
    data = {"name": "DuplicateTest", "unit": "x", "data_type": "number", "color": "#000"}
    authenticated_client.post("/metrics", data=data, follow_redirects=True)
    response = authenticated_client.post("/metrics", data=data, follow_redirects=True)
    assert response.status_code == 409


def test_delete_custom_metric(authenticated_client):
    authenticated_client.post(
        "/metrics",
        data={"name": "CustomToDelete", "unit": "x", "data_type": "number", "color": "#000000"},
        follow_redirects=True,
    )
    metrics = authenticated_client.get("/api/v1/metrics").json()
    custom_metric_id = next(m["id"] for m in metrics if m["name"] == "CustomToDelete")
    response = authenticated_client.delete(f"/metrics/{custom_metric_id}")
    assert response.status_code == 200
