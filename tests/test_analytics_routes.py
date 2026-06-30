class TestAnalyticsRoutes:
    def test_analytics_redirects_anonymous(self, client):
        response = client.get("/analytics", follow_redirects=False)
        assert response.status_code in (303, 302)

    def test_analytics_page_loads_authenticated(self, authenticated_client):
        response = authenticated_client.get("/analytics")
        assert response.status_code == 200
        assert "Analytics" in response.text
        assert "Physiological Trends" in response.text

    def test_analytics_data_htmx_endpoint(self, authenticated_client):
        response = authenticated_client.get("/analytics/data?range=7d")
        assert response.status_code == 200
        assert "trendsChart" in response.text

    def test_analytics_data_default_range(self, authenticated_client):
        response = authenticated_client.get("/analytics/data")
        assert response.status_code == 200
