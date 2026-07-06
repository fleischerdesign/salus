def test_list_entries_requires_auth(client):
    response = client.get("/entries", follow_redirects=False)
    assert response.status_code == 303


def test_list_entries_empty(authenticated_client):
    authenticated_client.post(
        "/metrics",
        data={"name": "Weight", "unit": "kg", "data_type": "number", "color": "#ef4444"},
        follow_redirects=True,
    )
    response = authenticated_client.get("/entries/13")
    assert response.status_code == 200


def test_create_and_list_entry(authenticated_client):
    authenticated_client.post(
        "/metrics",
        data={"name": "Weight", "unit": "kg", "data_type": "number", "color": "#ef4444"},
        follow_redirects=True,
    )
    response = authenticated_client.post(
        "/entries",
        data={"value": "80.5", "metric_type_id": "13"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "80.5" in response.text


def test_delete_entry(authenticated_client):
    authenticated_client.post(
        "/metrics",
        data={"name": "Weight", "unit": "kg", "data_type": "number", "color": "#ef4444"},
        follow_redirects=True,
    )
    authenticated_client.post(
        "/entries",
        data={"value": "80.5", "metric_type_id": "13"},
        follow_redirects=True,
    )
    response = authenticated_client.delete("/entries/1")
    assert response.status_code == 200
