"""Tests for mood tracking — entry CRUD, tags, stats."""

from datetime import date, timedelta


class TestMoodRoutes:
    def test_tags(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/mood/tags")
        assert resp.status_code == 200
        tags = resp.json()
        assert len(tags) >= 0

    def test_log_and_get(self, authenticated_client):
        today = date.today().isoformat()
        resp = authenticated_client.post("/api/v1/mood", json={
            "mood_score": 7,
            "energy_level": 6,
            "stress_level": 3,
            "notes": "Feeling good",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["mood_score"] == 7
        assert data["entry_date"] == today

        resp = authenticated_client.get("/api/v1/mood")
        assert resp.status_code == 200
        entries = resp.json()
        assert len(entries) == 1
        assert entries[0]["mood_score"] == 7

    def test_get_by_date(self, authenticated_client):
        authenticated_client.post("/api/v1/mood", json={"mood_score": 5})
        today = date.today().isoformat()
        resp = authenticated_client.get(f"/api/v1/mood/{today}")
        assert resp.status_code == 200
        assert resp.json()["mood_score"] == 5

    def test_stats(self, authenticated_client):
        for i in range(5):
            d = (date.today() - timedelta(days=i)).isoformat()
            authenticated_client.post("/api/v1/mood", json={
                "mood_score": 6 + i,
                "entry_date": d,
            })
        resp = authenticated_client.get("/api/v1/mood/stats?days=7")
        assert resp.status_code == 200
        stats = resp.json()
        assert stats["total_entries"] == 5

    def test_requires_auth(self, client):
        resp = client.get("/api/v1/mood", follow_redirects=False)
        assert resp.status_code in (401, 403)
