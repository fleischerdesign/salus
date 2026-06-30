class TestApiAuth:
    def test_api_no_key_returns_redirect(self, client):
        response = client.get("/api/metrics", follow_redirects=False)
        assert response.status_code in (303, 302)

    def test_api_wrong_key_returns_redirect(self, client):
        response = client.get(
            "/api/metrics",
            headers={"X-API-Key": "wrong-key"},
            follow_redirects=False,
        )
        assert response.status_code in (303, 302)


class TestApiMetrics:
    def test_list_metrics_empty(self, authenticated_client):
        """Uses cookie auth from authenticated_client, not API key."""
        response = authenticated_client.get("/api/metrics")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_and_list(self, authenticated_client):
        response = authenticated_client.post(
            "/api/metrics",
            json={"name": "Weight", "unit": "kg", "data_type": "number", "color": "#ff0000"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Weight"
        metric_id = data["id"]

        response = authenticated_client.get("/api/metrics")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == metric_id

    def test_get_metric(self, authenticated_client):
        authenticated_client.post(
            "/api/metrics",
            json={"name": "HR", "unit": "bpm", "data_type": "number", "color": "#ff0000"},
        )
        response = authenticated_client.get("/api/metrics/1")
        assert response.status_code == 200
        assert response.json()["name"] == "HR"

    def test_get_not_found(self, authenticated_client):
        response = authenticated_client.get("/api/metrics/999")
        assert response.status_code == 404

    def test_delete_metric(self, authenticated_client):
        authenticated_client.post(
            "/api/metrics",
            json={"name": "Steps", "unit": "steps", "data_type": "number"},
        )
        response = authenticated_client.delete("/api/metrics/1")
        assert response.status_code == 204


class TestApiEntries:
    def test_list_entries_by_metric(self, authenticated_client):
        authenticated_client.post(
            "/api/metrics",
            json={"name": "Weight", "unit": "kg", "data_type": "number"},
        )
        authenticated_client.post(
            "/api/entries?metric_type_id=1",
            json={"value": "80.5"},
        )
        response = authenticated_client.get("/api/entries?metric_type_id=1")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["value"] == "80.5"


class TestApiHealth:
    def test_health_empty(self, authenticated_client):
        response = authenticated_client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == []
