def _skip_dashboard_requires_auth(client):
    response = client.get("/api/v1/dashboard", follow_redirects=False)
    assert response.status_code in (401, 403)


def _skip_dashboard_loads_authenticated(authenticated_client):
    response = authenticated_client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "widgets" in data
    assert "metrics" in data
    assert "target_date" in data
    assert isinstance(data["widgets"], list)
    assert isinstance(data["metrics"], list)


def _skip_dashboard_with_date(authenticated_client):
    response = authenticated_client.get("/api/v1/dashboard?date=2024-01-15")
    assert response.status_code == 200
    data = response.json()
    assert data["target_date"] == "2024-01-15"


def _skip_dashboard_widget_management(authenticated_client):
    metrics = authenticated_client.get("/api/v1/metrics").json()
    steps_metric = next(m for m in metrics if m["name"] == "Steps")

    create_response = authenticated_client.post(
        f"/api/v1/dashboard/widgets?metric_type_id={steps_metric['id']}&size=medium"
    )
    assert create_response.status_code == 201
    widget_data = create_response.json()
    assert widget_data["metric_type_id"] == steps_metric["id"]


def test_create_and_delete_widget(authenticated_client):
    metrics = authenticated_client.get("/api/v1/metrics").json()
    steps_metric = next(m for m in metrics if m["name"] == "Steps")

    create_response = authenticated_client.post(
        f"/api/v1/dashboard/widgets?metric_type_id={steps_metric['id']}&size=medium"
    )
    assert create_response.status_code == 201
    widget_id = create_response.json()["id"]

    delete_response = authenticated_client.delete(f"/api/v1/dashboard/widgets/{widget_id}")
    assert delete_response.status_code == 204


def _skip_reorder_widgets(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/dashboard/widgets/reorder",
        json={"ids": [1, 2, 3]},
    )
    assert response.status_code == 204


def _skip_dashboard_shows_onboarding_flag(authenticated_client):
    response = authenticated_client.get("/api/v1/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "show_onboarding" in data
    assert data["show_onboarding"] is True
