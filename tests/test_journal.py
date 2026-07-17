"""Tests for journal entries — CRUD, ownership."""

from datetime import date


class TestJournalRoutes:
    def test_list_empty(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/journal")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_and_list(self, authenticated_client):
        today = date.today().isoformat()
        resp = authenticated_client.post("/api/v1/journal", json={
            "title": "Monday",
            "content": "Started a new habit today.",
            "mood_score": 8,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Monday"
        assert data["entry_date"] == today
        entry_id = data["id"]

        resp = authenticated_client.get("/api/v1/journal")
        assert resp.status_code == 200
        entries = resp.json()
        assert len(entries) == 1
        assert entries[0]["id"] == entry_id

    def test_update_entry(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/journal", json={
            "content": "Original content",
        })
        entry_id = resp.json()["id"]

        resp = authenticated_client.put(f"/api/v1/journal/{entry_id}", json={
            "content": "Updated content",
            "title": "New Title",
        })
        assert resp.status_code == 200
        assert resp.json()["content"] == "Updated content"
        assert resp.json()["title"] == "New Title"

    def test_delete_entry(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/journal", json={
            "content": "Delete me",
        })
        entry_id = resp.json()["id"]

        resp = authenticated_client.delete(f"/api/v1/journal/{entry_id}")
        assert resp.status_code == 204

        resp = authenticated_client.get("/api/v1/journal")
        assert resp.json() == []

    def test_private_entry(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/journal", json={
            "content": "Secret",
            "is_private": True,
        })
        assert resp.status_code == 201
        assert resp.json()["is_private"] is True

    def test_requires_auth(self, client):
        resp = client.get("/api/v1/journal", follow_redirects=False)
        assert resp.status_code in (401, 403)
