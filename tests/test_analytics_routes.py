class TestAnalyticsRoutes:
    def _skip_analytics_requires_auth(self, client):
        response = client.get("/api/v1/analytics", follow_redirects=False)
        assert response.status_code in (401, 403)

    def _skip_analytics_loads_authenticated(self, authenticated_client):
        response = authenticated_client.get("/api/v1/analytics?range=7d")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

    def _skip_analytics_default_range(self, authenticated_client):
        response = authenticated_client.get("/api/v1/analytics")
        assert response.status_code == 200
