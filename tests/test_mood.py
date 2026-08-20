"""Tests for mood tracking — entry CRUD, tags, stats."""

from datetime import date, datetime, timedelta, timezone


def _log_mood(client, payload: dict) -> dict:
    """Create a mood entry via the generic auto-CRUD write surface."""
    resp = client.post("/api/v1/sync/push", json={
        "operations": [{"type": "create", "entity": "mood_entry", "data": payload}],
    })
    assert resp.status_code == 200
    return resp.json()["results"][0]


class TestMoodRoutes:
    def test_tags(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/mood/tags")
        assert resp.status_code == 200
        tags = resp.json()
        assert len(tags) >= 0

    def test_log_and_get(self, authenticated_client):
        today = date.today().isoformat()
        result = _log_mood(authenticated_client, {
            "entry_date": today,
            "mood_score": 7,
            "energy_level": 6,
            "stress_level": 3,
            "notes": "Feeling good",
        })
        assert result["status"] == "created"
        assert result["record"]["mood_score"] == 7
        assert result["record"]["entry_date"] == today

        resp = authenticated_client.get("/api/v1/mood")
        assert resp.status_code == 200
        entries = resp.json()
        assert len(entries) == 1
        assert entries[0]["mood_score"] == 7

    def test_get_by_date(self, authenticated_client):
        today = date.today().isoformat()
        _log_mood(authenticated_client, {"entry_date": today, "mood_score": 5})
        resp = authenticated_client.get(f"/api/v1/mood/{today}")
        assert resp.status_code == 200
        assert resp.json()["mood_score"] == 5

    def test_stats(self, authenticated_client):
        # Log relative to the UTC day (matching the default UTC user timezone
        # used by user_today) — not the server's local date, which can drift
        # one day ahead of UTC and drop the "today" entry.
        utc_today = datetime.now(timezone.utc).date()
        for i in range(5):
            d = (utc_today - timedelta(days=i)).isoformat()
            _log_mood(authenticated_client, {
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
