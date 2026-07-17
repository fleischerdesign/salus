"""Tests for habits — CRUD, toggle check, stats, ownership."""

from datetime import date


class TestHabitRoutes:
    def test_list_empty(self, authenticated_client):
        resp = authenticated_client.get("/api/v1/habits")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_and_list(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/habits", json={
            "name": "Morning Stretch",
            "frequency": "daily",
            "color": "#4f46e5",
            "icon": "self-improvement",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Morning Stretch"
        assert data["frequency"] == "daily"
        habit_id = data["id"]

        resp = authenticated_client.get("/api/v1/habits")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["id"] == habit_id

    def test_get_habit(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/habits", json={
            "name": "Read",
            "frequency": "daily",
            "color": "#f97316",
            "icon": "menu-book",
        })
        habit_id = resp.json()["id"]

        resp = authenticated_client.get(f"/api/v1/habits/{habit_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Read"

    def test_update_habit(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/habits", json={
            "name": "Old Name",
            "frequency": "daily",
            "color": "#4f46e5",
            "icon": "check-circle",
        })
        habit_id = resp.json()["id"]

        resp = authenticated_client.put(f"/api/v1/habits/{habit_id}", json={
            "name": "New Name",
            "description": "Updated desc",
        })
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"
        assert resp.json()["description"] == "Updated desc"

    def test_delete_habit(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/habits", json={
            "name": "Delete Me",
            "frequency": "daily",
            "color": "#4f46e5",
            "icon": "check-circle",
        })
        habit_id = resp.json()["id"]

        resp = authenticated_client.delete(f"/api/v1/habits/{habit_id}")
        assert resp.status_code == 204

        resp = authenticated_client.get(f"/api/v1/habits/{habit_id}")
        assert resp.status_code == 404

    def test_toggle_check(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/habits", json={
            "name": "Toggle",
            "frequency": "daily",
            "color": "#4f46e5",
            "icon": "check-circle",
        })
        habit_id = resp.json()["id"]

        resp = authenticated_client.post(f"/api/v1/habits/{habit_id}/check")
        assert resp.status_code == 200
        data = resp.json()
        assert data["completed"] is True
        assert data["current_streak"] == 1

        resp = authenticated_client.get("/api/v1/habits")
        stats = resp.json()[0]
        assert stats["current_streak"] == 1
        assert stats["today_completed"] is True

        resp = authenticated_client.post(f"/api/v1/habits/{habit_id}/check")
        assert resp.status_code == 200
        assert resp.json()["completed"] is False

    def test_requires_auth(self, client):
        resp = client.get("/api/v1/habits", follow_redirects=False)
        assert resp.status_code in (401, 403)

    def test_cannot_access_other_user_habit(self, authenticated_client):
        resp = authenticated_client.post("/api/v1/habits", json={
            "name": "Mine",
            "frequency": "daily",
            "color": "#4f46e5",
            "icon": "check-circle",
        })
        habit_id = resp.json()["id"]

        headers = authenticated_client.headers
        authenticated_client.headers = {}
        try:
            reg = authenticated_client.post("/api/v1/auth/register", json={
                "username": "bob",
                "password": "secret123",
                "email": "bob@salus.local",
                "display_name": "Bob",
            })
            bob_token = reg.json().get("token", "")

            authenticated_client.headers = {"Authorization": f"Bearer {bob_token}"}
            resp = authenticated_client.get(f"/api/v1/habits/{habit_id}")
            assert resp.status_code == 404
        finally:
            authenticated_client.headers = headers
