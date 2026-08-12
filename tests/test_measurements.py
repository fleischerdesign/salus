def test_list_measurements_requires_auth(client):
    response = client.get("/api/v1/measurements", follow_redirects=False)
    assert response.status_code in (401, 403)


def test_list_measurements_empty(authenticated_client):
    response = authenticated_client.get("/api/v1/measurements?metric_code=weight")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_list_measurement(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/measurements",
        json={"metric_code": "weight", "value_text": "80.5"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["value_text"] == "80.5"
    assert data["metric_code"] == "weight"

    response = authenticated_client.get("/api/v1/measurements?metric_code=weight")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["value_text"] == "80.5"


def test_update_measurement(authenticated_client):
    create_resp = authenticated_client.post(
        "/api/v1/measurements",
        json={"metric_code": "weight", "value_text": "80.5"},
    )
    entry_id = create_resp.json()["id"]

    response = authenticated_client.put(
        f"/api/v1/measurements/{entry_id}",
        json={"value_text": "82.0", "notes": "updated"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value_text"] == "82.0"
    assert data["notes"] == "updated"


def test_delete_measurement(authenticated_client):
    create_resp = authenticated_client.post(
        "/api/v1/measurements",
        json={"metric_code": "weight", "value_text": "80.5"},
    )
    entry_id = create_resp.json()["id"]

    response = authenticated_client.delete(f"/api/v1/measurements/{entry_id}")
    assert response.status_code == 204

    list_resp = authenticated_client.get("/api/v1/measurements?metric_code=weight")
    assert list_resp.json() == []


def test_update_measurement_not_found(authenticated_client):
    response = authenticated_client.put(
        "/api/v1/measurements/99999",
        json={"value_text": "1"},
    )
    assert response.status_code == 404


def test_delete_measurement_not_found(authenticated_client):
    response = authenticated_client.delete("/api/v1/measurements/99999")
    assert response.status_code == 404


def test_create_measurement_unknown_metric_rejected(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/measurements",
        json={"metric_code": "nonexistent", "value_text": "1"},
    )
    assert response.status_code == 400
