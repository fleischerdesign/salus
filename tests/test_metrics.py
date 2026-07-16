def _hard_delete_preference(client, code: str) -> None:
    from sqlmodel import Session, select
    from salus.models.metric_preference import UserMetricPreference
    from salus.main import app as fastapi_app

    engine = fastapi_app.state.engine
    with Session(engine) as s:
        stmt = select(UserMetricPreference).where(UserMetricPreference.metric_code == code)
        for pref in s.exec(stmt).all():
            s.delete(pref)
        s.commit()


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


def test_create_and_list_metric(authenticated_client):
    _hard_delete_preference(authenticated_client, "chest")
    response = authenticated_client.post(
        "/api/v1/metrics",
        json={"name": "chest", "unit": "cm", "data_type": "number", "color": "#ef4444"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Chest"
    assert data["icon"] == "monitoring"

    response = authenticated_client.get("/api/v1/metrics")
    names = [m["name"] for m in response.json()]
    assert "Chest" in names


def test_create_metric_with_icon(authenticated_client):
    _hard_delete_preference(authenticated_client, "waist")
    response = authenticated_client.post(
        "/api/v1/metrics",
        json={
            "name": "waist",
            "unit": "cm",
            "data_type": "number",
            "color": "#ef4444",
            "icon": "monitor-weight",
        },
    )
    assert response.status_code == 201
    assert response.json()["icon"] == "monitor-weight"


def test_delete_system_metric_rejected(authenticated_client):
    response = authenticated_client.delete("/api/v1/metrics/steps")
    assert response.status_code == 204


def test_create_duplicate_rejected(authenticated_client):
    _hard_delete_preference(authenticated_client, "hip")
    data = {"name": "hip", "unit": "cm", "data_type": "number", "color": "#000"}
    authenticated_client.post("/api/v1/metrics", json=data)
    response = authenticated_client.post("/api/v1/metrics", json=data)
    assert response.status_code == 409


def test_delete_custom_metric(authenticated_client):
    _hard_delete_preference(authenticated_client, "body_fat")
    authenticated_client.post(
        "/api/v1/metrics",
        json={"name": "body_fat", "unit": "%", "data_type": "number", "color": "#000000"},
    )
    response = authenticated_client.delete("/api/v1/metrics/body_fat")
    assert response.status_code == 204


def test_update_metric(authenticated_client):
    _hard_delete_preference(authenticated_client, "stress")
    create_resp = authenticated_client.post(
        "/api/v1/metrics",
        json={"name": "stress", "unit": "", "data_type": "number", "color": "#000"},
    )
    metric_code = create_resp.json()["id"]
    response = authenticated_client.put(
        f"/api/v1/metrics/{metric_code}",
        json={"name": "stress", "unit": "", "data_type": "number", "color": "#ff0000", "icon": "monitor-weight"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Stress"
    assert data["color"] == "#ff0000"
    assert data["icon"] == "monitor-weight"
