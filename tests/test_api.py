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

    def test_list_returns_definitions(self, authenticated_client):
        response = authenticated_client.get("/api/v1/metrics")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 18
        codes = {m["id"] for m in data}
        assert "steps" in codes
        assert "weight" in codes
        assert "water" in codes

    def test_get_metric(self, authenticated_client):
        response = authenticated_client.get("/api/v1/metrics/steps")
        assert response.status_code == 200
        assert response.json()["name"] == "Steps"

    def test_get_not_found(self, authenticated_client):
        response = authenticated_client.get("/api/v1/metrics/nonexistent")
        assert response.status_code == 404

    def test_update_preference(self, authenticated_client):
        response = authenticated_client.put(
            "/api/v1/metrics/water",
            json={"name": "water", "color": "#ff0000", "icon": "water_drop"},
        )
        assert response.status_code == 200
        assert response.json()["color"] == "#ff0000"


class TestApiEntries:
    def test_list_entries_by_metric(self, authenticated_client):
        authenticated_client.post(
            "/api/v1/entries?metric_code=weight",
            json={"value": "80.5"},
        )
        response = authenticated_client.get("/api/v1/entries?metric_code=weight")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["entries"][0]["value"] == "80.5"



