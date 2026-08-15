def _create_widget(client, metric_code: str) -> dict:
    resp = client.post("/api/v1/dashboard-widgets", json={
        "widget_type": "metric",
        "metric_code": metric_code,
        "position": 0,
        "size": "medium",
        "config_json": "{}",
        "is_visible": True,
    })
    assert resp.status_code == 201
    return resp.json()


def test_dashboard_widget_management(authenticated_client):
    metrics = authenticated_client.get("/api/v1/metrics").json()
    steps_metric = next(m for m in metrics if m["name"] == "Steps")

    widget_data = _create_widget(authenticated_client, steps_metric["id"])
    assert widget_data["metric_code"] == steps_metric["id"]


def test_create_and_delete_widget(authenticated_client):
    metrics = authenticated_client.get("/api/v1/metrics").json()
    steps_metric = next(m for m in metrics if m["name"] == "Steps")

    widget = _create_widget(authenticated_client, steps_metric["id"])
    widget_id = widget["id"]

    delete_response = authenticated_client.delete(f"/api/v1/dashboard-widgets/{widget_id}")
    assert delete_response.status_code == 204
