import pytest
from fastapi.testclient import TestClient

from salus.config import settings
from salus.main import app


@pytest.fixture
def webhook_client(client):
    """client fixture with webhook auth header preset."""
    client.headers = {"Authorization": f"Bearer {settings.api_token}"}
    return client


def _get_metric_id(client, name: str) -> str:
    resp = client.get("/api/v1/metrics")
    assert resp.status_code == 200
    for mt in resp.json():
        if mt["name"] == name:
            return mt["id"]
    raise ValueError(f"Metric type {name} not found")


def test_webhook_rejects_without_token():
    client = TestClient(app)
    response = client.post("/webhook", json={})
    assert response.status_code == 401


def test_webhook_rejects_invalid_token():
    client = TestClient(app, headers={"Authorization": "Bearer wrong-token"})
    response = client.post("/webhook", json={})
    assert response.status_code == 401


def test_webhook_accepts_x_api_token_header(client):
    payload = {
        "steps": [
            {"count": 5000, "start_time": "2026-01-01T08:00:00", "end_time": "2026-01-01T09:00:00"}
        ],
    }
    response = client.post("/webhook", json=payload, headers={"X-API-Token": settings.api_token})
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"

    client.headers = {"Authorization": f"Bearer {settings.api_token}"}
    steps_id = _get_metric_id(client, "Steps")

    steps_code = _get_metric_id(client, "Steps")
    entries_resp = client.get(f"/api/v1/entries?metric_code={steps_code}")
    assert entries_resp.status_code == 200
    data = entries_resp.json()
    assert data["total"] == 1
    assert float(data["entries"][0]["value"]) == 5000.0


def test_webhook_inserts_health_records(webhook_client):
    payload = {
        "steps": [
            {"count": 8500, "start_time": "2026-06-24T08:00:00", "end_time": "2026-06-24T22:00:00"}
        ],
    }
    response = webhook_client.post("/webhook", json=payload)
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"

    steps_code = _get_metric_id(webhook_client, "Steps")
    entries_resp = webhook_client.get(f"/api/v1/entries?metric_code={steps_code}")
    assert entries_resp.status_code == 200
    data = entries_resp.json()
    assert data["total"] == 1
    assert float(data["entries"][0]["value"]) == 8500.0


def test_webhook_deduplicates(webhook_client):
    payload = {
        "steps": [
            {"id": "step-1", "count": 8500, "start_time": "2026-06-24T08:00:00"}
        ],
    }
    response = webhook_client.post("/webhook", json=payload)
    assert response.status_code == 202

    response = webhook_client.post("/webhook", json=payload)
    assert response.status_code == 202

    steps_code = _get_metric_id(webhook_client, "Steps")
    entries_resp = webhook_client.get(f"/api/v1/entries?metric_code={steps_code}")
    assert entries_resp.status_code == 200
    assert entries_resp.json()["total"] == 1


def test_webhook_rejects_invalid_json(webhook_client):
    response = webhook_client.post("/webhook", content=b"not json")
    assert response.status_code in (400, 422)


def test_webhook_handles_multiple_records(webhook_client):
    payload = {
        "steps": [{"count": 5000, "start_time": "2026-01-01T08:00:00"}],
        "heart_rate": [
            {"bpm": 72, "start_time": "2026-01-01T08:00:00"},
            {"bpm": 75, "start_time": "2026-01-01T08:30:00"},
        ],
        "weight": [{"weight_kg": 80.5, "start_time": "2026-01-01T08:00:00"}],
    }
    response = webhook_client.post("/webhook", json=payload)
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"

    steps_code = _get_metric_id(webhook_client, "Steps")
    steps_resp = webhook_client.get(f"/api/v1/entries?metric_code={steps_code}")
    assert steps_resp.json()["total"] == 1

    hr_code = _get_metric_id(webhook_client, "Heart Rate")
    hr_resp = webhook_client.get(f"/api/v1/entries?metric_code={hr_code}")
    assert hr_resp.json()["total"] == 2

    weight_code = _get_metric_id(webhook_client, "Weight")
    weight_resp = webhook_client.get(f"/api/v1/entries?metric_code={weight_code}")
    assert weight_resp.json()["total"] == 1
