def test_dashboard_widget_management(authenticated_client):
    metrics = authenticated_client.get("/api/v1/metrics").json()
    steps_metric = next(m for m in metrics if m["name"] == "Steps")

    create_response = authenticated_client.post(
        f"/api/v1/dashboard/widgets?metric_code={steps_metric['id']}&size=medium"
    )
    assert create_response.status_code == 201
    widget_data = create_response.json()
    assert widget_data["metric_code"] == steps_metric["id"]


def test_create_and_delete_widget(authenticated_client):
    metrics = authenticated_client.get("/api/v1/metrics").json()
    steps_metric = next(m for m in metrics if m["name"] == "Steps")

    create_response = authenticated_client.post(
        f"/api/v1/dashboard/widgets?metric_code={steps_metric['id']}&size=medium"
    )
    assert create_response.status_code == 201
    widget_id = create_response.json()["id"]

    delete_response = authenticated_client.delete(f"/api/v1/dashboard/widgets/{widget_id}")
    assert delete_response.status_code == 204
