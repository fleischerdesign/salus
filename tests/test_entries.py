def test_list_entries_requires_auth(client):
    response = client.get("/api/v1/entries", follow_redirects=False)
    assert response.status_code in (401, 403)


def test_list_entries_empty(authenticated_client):
    response = authenticated_client.get("/api/v1/entries?metric_code=weight")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["entries"] == []


def test_create_and_list_entry(authenticated_client):
    response = authenticated_client.post(
        "/api/v1/entries?metric_code=weight",
        json={"value": "80.5"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["value"] == "80.5"
    assert data["metric_code"] == "weight"

    response = authenticated_client.get("/api/v1/entries?metric_code=weight")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["entries"][0]["value"] == "80.5"


def test_update_entry(authenticated_client):
    create_resp = authenticated_client.post(
        "/api/v1/entries?metric_code=weight",
        json={"value": "80.5"},
    )
    entry_id = create_resp.json()["id"]

    response = authenticated_client.put(
        f"/api/v1/entries/{entry_id}",
        json={"value": "82.0", "notes": "updated"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["value"] == "82.0"
    assert data["notes"] == "updated"


def test_delete_entry(authenticated_client):
    create_resp = authenticated_client.post(
        "/api/v1/entries?metric_code=weight",
        json={"value": "80.5"},
    )
    entry_id = create_resp.json()["id"]

    response = authenticated_client.delete(f"/api/v1/entries/{entry_id}")
    assert response.status_code == 204

    list_resp = authenticated_client.get("/api/v1/entries?metric_code=weight")
    assert list_resp.json()["total"] == 0


def test_update_entry_not_found(authenticated_client):
    response = authenticated_client.put(
        "/api/v1/entries/99999",
        json={"value": "1"},
    )
    assert response.status_code == 404


def test_delete_entry_not_found(authenticated_client):
    response = authenticated_client.delete("/api/v1/entries/99999")
    assert response.status_code == 404


def test_pagination(authenticated_client):
    for i in range(30):
        authenticated_client.post(
            "/api/v1/entries?metric_code=weight",
            json={"value": str(i)},
        )

    response = authenticated_client.get(
        "/api/v1/entries?metric_code=weight&page=1&per_page=10"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 30
    assert data["page"] == 1
    assert data["per_page"] == 10
    assert data["total_pages"] == 3
    assert len(data["entries"]) == 10

    response = authenticated_client.get(
        "/api/v1/entries?metric_code=weight&page=3&per_page=10"
    )
    data = response.json()
    assert len(data["entries"]) == 10
