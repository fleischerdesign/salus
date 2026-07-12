class TestApiAuth:
    def test_api_no_key_returns_unauthorized(self, client):
        response = client.get("/api/v1/metrics", follow_redirects=False)
        assert response.status_code == 401
        assert response.json() == {"error": "Not authenticated"}

    def test_api_wrong_key_returns_unauthorized(self, client):
        response = client.get(
            "/api/v1/metrics",
            headers={"X-API-Key": "wrong-key"},
            follow_redirects=False,
        )
        assert response.status_code == 401
        assert response.json() == {"error": "Invalid or expired token"}


class TestApiMetrics:
    def test_list_metrics_has_pre_seeded(self, authenticated_client):
        response = authenticated_client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 12
        names = {m["name"] for m in data}
        assert "Steps" in names
        assert "Heart Rate" in names
        assert "Weight" in names

    def test_create_and_list(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/metrics",
            json={"name": "CustomMetric", "unit": "kg", "data_type": "number", "color": "#ff0000"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "CustomMetric"

        response = authenticated_client.get("/api/v1/metrics")
        assert response.status_code == 200
        metrics = response.json()
        names = [m["name"] for m in metrics]
        assert "CustomMetric" in names

    def test_get_metric(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/metrics",
            json={"name": "HR", "unit": "bpm", "data_type": "number", "color": "#ff0000"},
        )
        metric_id = response.json()["id"]
        response = authenticated_client.get(f"/api/v1/metrics/{metric_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "HR"

    def test_get_not_found(self, authenticated_client):
        response = authenticated_client.get("/api/v1/metrics/999")
        assert response.status_code == 404

    def test_delete_metric(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/metrics",
            json={"name": "ToDelete", "unit": "steps", "data_type": "number"},
        )
        metric_id = response.json()["id"]
        response = authenticated_client.delete(f"/api/v1/metrics/{metric_id}")
        assert response.status_code == 204


class TestApiEntries:
    def test_list_entries_by_metric(self, authenticated_client):
        response = authenticated_client.post(
            "/api/v1/metrics",
            json={"name": "CustomWeight", "unit": "kg", "data_type": "number"},
        )
        metric_id = response.json()["id"]
        authenticated_client.post(
            f"/api/v1/entries?metric_type_id={metric_id}",
            json={"value": "80.5"},
        )
        response = authenticated_client.get(f"/api/v1/entries?metric_type_id={metric_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["entries"][0]["value"] == "80.5"


class TestApiHealth:
    def _skip_health_empty(self, authenticated_client):
        response = authenticated_client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json() == []
