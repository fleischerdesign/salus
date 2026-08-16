class TestUserSourceStatusAPI:
    def test_source_status_requires_auth(self, client):
        response = client.get("/api/v1/settings/source-status")
        assert response.status_code in (401, 403)

    def test_source_status_empty(self, authenticated_client):
        response = authenticated_client.get("/api/v1/settings/source-status")
        assert response.status_code == 200
        assert response.json() == []

    def test_set_and_get_source_status(self, authenticated_client):
        put_res = authenticated_client.put(
            "/api/v1/settings/source-status",
            json={"source": "health_connect", "connected": True},
        )
        assert put_res.status_code == 200
        data = put_res.json()
        assert data["source"] == "health_connect"
        assert data["connected"] is True

        get_res = authenticated_client.get("/api/v1/settings/source-status")
        assert get_res.status_code == 200
        statuses = get_res.json()
        assert len(statuses) == 1
        assert statuses[0]["source"] == "health_connect"
        assert statuses[0]["connected"] is True

    def test_set_source_status_is_idempotent(self, authenticated_client):
        first = authenticated_client.put(
            "/api/v1/settings/source-status",
            json={"source": "oura", "connected": True},
        ).json()
        second = authenticated_client.put(
            "/api/v1/settings/source-status",
            json={"source": "oura", "connected": False},
        ).json()

        assert first["source"] == second["source"] == "oura"
        assert first["connected"] is True
        assert second["connected"] is False

        get_res = authenticated_client.get("/api/v1/settings/source-status")
        assert get_res.status_code == 200
        statuses = get_res.json()
        assert len(statuses) == 1
        assert statuses[0]["connected"] is False
