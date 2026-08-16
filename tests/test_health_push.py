from datetime import datetime, timezone

from salus.services.constants import SOURCE_HEALTH_CONNECT


def _measurement(external_id: str, value: float, metric_code: str = "steps") -> dict:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "id": f"uuid-{external_id}",
        "metric_code": metric_code,
        "source": SOURCE_HEALTH_CONNECT,
        "value_numeric": value,
        "start_time": now,
        "external_id": external_id,
        "created_at": now,
        "updated_at": now,
    }


def test_health_push_requires_auth(client):
    response = client.post("/api/v1/sync/health-push", json={"measurements": []})
    assert response.status_code in (401, 403)


def test_health_push_inserts(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/sync/health-push",
        json={"measurements": [_measurement("hc_steps_a", 100.0)]},
    )
    assert response.status_code == 200
    assert response.json() == {"inserted": 1, "duplicates": 0}

    list_resp = authenticated_client.get("/api/v1/measurements?metric_code=steps")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["value_numeric"] == 100.0


def test_health_push_is_idempotent_by_external_id(authenticated_client):
    first = authenticated_client.post(
        "/api/v1/sync/health-push",
        json={"measurements": [_measurement("hc_steps_b", 100.0)]},
    )
    assert first.json() == {"inserted": 1, "duplicates": 0}

    # A re-seed pushes the same external_id with a new local id and a new value.
    reseed = _measurement("hc_steps_b", 120.0)
    reseed["id"] = "uuid-other"
    second = authenticated_client.post(
        "/api/v1/sync/health-push",
        json={"measurements": [reseed]},
    )
    assert second.json() == {"inserted": 0, "duplicates": 1}

    list_resp = authenticated_client.get("/api/v1/measurements?metric_code=steps")
    body = list_resp.json()
    assert len(body) == 1
    assert body[0]["value_numeric"] == 120.0
