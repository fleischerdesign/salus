"""Tests for achievements — definitions, progress, streaks."""


class TestAchievementRoutes:
    def test_list_achievements(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/achievements")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        if len(data) > 0:
            for a in data:
                assert "code" in a
                assert "title" in a
                assert "tier" in a

    def test_unlocked_empty_for_new_user(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/achievements/unlocked")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_streaks(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/streaks")
        assert resp.status_code == 200
        data = resp.json()
        assert "mood" in data
        assert "habits" in data

    def test_requires_auth(self, client):
        resp = client.get("/api/v1/achievements", follow_redirects=False)
        assert resp.status_code in (401, 403)
