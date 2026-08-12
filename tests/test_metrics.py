from sqlmodel import Session, select

from salus.main import app as fastapi_app
from salus.models.metric_preference import UserMetricPreference


def _delete_preference(metric_code: str) -> None:
    with Session(fastapi_app.state.engine) as s:
        for pref in s.exec(
            select(UserMetricPreference).where(
                UserMetricPreference.metric_code == metric_code
            )
        ).all():
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


def test_create_and_list_metric_preference(authenticated_client):
    _delete_preference("chest")
    response = authenticated_client.post(
        "/api/v1/user-metric-preferences",
        json={"metric_code": "chest", "color": "#ef4444"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["metric_code"] == "chest"
    assert data["color"] == "#ef4444"

    response = authenticated_client.get("/api/v1/metrics")
    names = [m["name"] for m in response.json()]
    assert "Chest" in names


def test_create_metric_preference_with_icon(authenticated_client):
    _delete_preference("waist")
    response = authenticated_client.post(
        "/api/v1/user-metric-preferences",
        json={"metric_code": "waist", "color": "#ef4444", "icon": "monitor-weight"},
    )
    assert response.status_code == 201
    assert response.json()["icon"] == "monitor-weight"


def test_create_unknown_metric_rejected(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/user-metric-preferences",
        json={"metric_code": "nonexistent", "color": "#000"},
    )
    assert response.status_code == 400


def test_create_duplicate_rejected(authenticated_client):
    _delete_preference("hip")
    data = {"metric_code": "hip", "color": "#000"}
    assert authenticated_client.post("/api/v1/user-metric-preferences", json=data).status_code == 201
    response = authenticated_client.post("/api/v1/user-metric-preferences", json=data)
    assert response.status_code == 400


def test_delete_metric_preference(authenticated_client):
    _delete_preference("body_fat")
    create_resp = authenticated_client.post(
        "/api/v1/user-metric-preferences",
        json={"metric_code": "body_fat", "color": "#000000"},
    )
    pref_id = create_resp.json()["id"]
    response = authenticated_client.delete(f"/api/v1/user-metric-preferences/{pref_id}")
    assert response.status_code == 204


def test_update_metric_preference(authenticated_client):
    _delete_preference("stress")
    create_resp = authenticated_client.post(
        "/api/v1/user-metric-preferences",
        json={"metric_code": "stress", "color": "#000"},
    )
    pref_id = create_resp.json()["id"]
    response = authenticated_client.patch(
        f"/api/v1/user-metric-preferences/{pref_id}",
        json={"color": "#ff0000", "icon": "monitor-weight"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["color"] == "#ff0000"
    assert data["icon"] == "monitor-weight"
