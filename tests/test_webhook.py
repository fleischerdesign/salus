import pytest
from fastapi.testclient import TestClient

from salus.config import settings
from salus.main import app


@pytest.fixture
def webhook_client(client):
    """client fixture with webhook auth header preset."""
    client.headers = {"Authorization": f"Bearer {settings.api_token}"}
    return client


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
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["inserted"] == 1


def test_webhook_inserts_health_records(webhook_client):
    payload = {
        "steps": [
            {"count": 8500, "start_time": "2026-06-24T08:00:00", "end_time": "2026-06-24T22:00:00"}
        ],
    }
    response = webhook_client.post("/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["inserted"] == 1
    assert data["duplicates"] == 0


def test_webhook_deduplicates(webhook_client):
    payload = {
        "steps": [
            {"id": "step-1", "count": 8500, "start_time": "2026-06-24T08:00:00"}
        ],
    }
    response = webhook_client.post("/webhook", json=payload)
    assert response.json()["inserted"] == 1

    response = webhook_client.post("/webhook", json=payload)
    data = response.json()
    assert data["inserted"] == 0
    assert data["duplicates"] == 1


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
    assert response.status_code == 200
    data = response.json()
    assert data["inserted"] == 4
    assert data["duplicates"] == 0
