def test_list_metrics_requires_auth(client):
    response = client.get("/metrics", follow_redirects=False)
    assert response.status_code == 303


def test_list_metrics_empty(authenticated_client):
    response = authenticated_client.get("/metrics")
    assert response.status_code == 200


def test_create_and_list_metric(authenticated_client):
    response = authenticated_client.post(
        "/metrics",
        data={"name": "Weight", "unit": "kg", "data_type": "number", "color": "#ef4444"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = authenticated_client.get("/metrics")
    assert "Weight" in response.text


def test_delete_metric(authenticated_client):
    authenticated_client.post(
        "/metrics",
        data={"name": "Weight", "unit": "kg", "data_type": "number", "color": "#ef4444"},
        follow_redirects=True,
    )
    response = authenticated_client.delete("/metrics/1")
    assert response.status_code == 200
