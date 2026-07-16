from starlette.testclient import TestClient


class TestAutoCRUD:
    def test_list_exercises(self, authenticated_client: TestClient):
        resp = authenticated_client.get("/api/v1/exercises")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_exercise_not_found(self, authenticated_client: TestClient):
        resp = authenticated_client.get("/api/v1/exercises/nonexistent")
        assert resp.status_code == 404
        assert "error" in resp.json()

    def test_create_and_delete_exercise(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/exercises", json={
            "name": "REST Test Exercise", "equipment": "barbell", "primary_muscles": "quadriceps,glutes",
        })
        assert resp.status_code == 201
        created = resp.json()
        assert created["name"] == "REST Test Exercise"
        item_id = created["id"]

        get_resp = authenticated_client.get(f"/api/v1/exercises/{item_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "REST Test Exercise"

        patch_resp = authenticated_client.patch(f"/api/v1/exercises/{item_id}", json={"name": "REST Updated Ex"})
        assert patch_resp.status_code == 200
        assert patch_resp.json()["name"] == "REST Updated Ex"

        del_resp = authenticated_client.delete(f"/api/v1/exercises/{item_id}")
        assert del_resp.status_code == 204

    def test_create_goal(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/goals", json={
            "metric_code": "steps",
            "target_value": 100.0,
            "direction": "increase",
            "frequency": "daily",
        })
        assert resp.status_code == 201

    def test_create_workout_plan(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/workout-plans", json={
            "name": "Push Day", "position": 0,
        })
        assert resp.status_code == 201
        assert resp.json()["name"] == "Push Day"

    def test_unauthorized_access(self, client: TestClient):
        resp = client.get("/api/v1/exercises")
        assert resp.status_code == 401

    def test_error_envelope_format(self, authenticated_client: TestClient):
        resp = authenticated_client.get("/api/v1/exercises/nonexistent-id")
        assert resp.status_code == 404
        error = resp.json()["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == "not_found"

    def test_patch_validation(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/exercises", json={
            "name": "Before Patch Ex", "equipment": "barbell", "primary_muscles": "biceps",
        })
        item_id = resp.json()["id"]

        resp = authenticated_client.patch(f"/api/v1/exercises/{item_id}", json={"name": "After Patch Ex"})
        assert resp.status_code == 200

    def test_delete_not_found(self, authenticated_client: TestClient):
        resp = authenticated_client.delete("/api/v1/exercises/nonexistent-id")
        assert resp.status_code == 404

    def test_create_requires_auth(self, client: TestClient):
        resp = client.post("/api/v1/exercises", json={"name": "X", "equipment": "kg", "primary_muscles": "chest"})
        assert resp.status_code == 401
