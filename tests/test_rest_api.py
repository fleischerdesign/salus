from starlette.testclient import TestClient


class TestAutoCRUD:
    def test_list_metric_types(self, authenticated_client: TestClient):
        resp = authenticated_client.get("/api/v1/metric-types")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_metric_type_not_found(self, authenticated_client: TestClient):
        resp = authenticated_client.get("/api/v1/metric-types/nonexistent")
        assert resp.status_code == 404
        assert "error" in resp.json()

    def test_create_and_delete_metric_type(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/metric-types", json={
            "name": "REST Test", "unit": "kg", "data_type": "number",
        })
        assert resp.status_code == 201
        created = resp.json()
        assert created["name"] == "REST Test"
        item_id = created["id"]

        get_resp = authenticated_client.get(f"/api/v1/metric-types/{item_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == "REST Test"

        patch_resp = authenticated_client.patch(f"/api/v1/metric-types/{item_id}", json={"name": "REST Updated"})
        assert patch_resp.status_code == 200
        assert patch_resp.json()["name"] == "REST Updated"

        del_resp = authenticated_client.delete(f"/api/v1/metric-types/{item_id}")
        assert del_resp.status_code == 204

    def test_create_exercise(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/exercises", json={
            "name": "Squat", "equipment": "barbell", "primary_muscles": "quadriceps,glutes",
        })
        assert resp.status_code == 201
        assert resp.json()["name"] == "Squat"

    def test_list_exercises(self, authenticated_client: TestClient):
        authenticated_client.post("/api/v1/exercises", json={
            "name": "Bench", "primary_muscles": "chest",
        })
        resp = authenticated_client.get("/api/v1/exercises")
        assert resp.status_code == 200
        exercises = resp.json()
        assert any(e["name"] == "Bench" for e in exercises)

    def test_create_goal(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/goals", json={
            "metric_type_id": "018f0000-0000-0000-0000-000000000001",
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
        resp = client.get("/api/v1/metric-types")
        assert resp.status_code == 401

    def test_error_envelope_format(self, authenticated_client: TestClient):
        resp = authenticated_client.get("/api/v1/metric-types/nonexistent-id")
        assert resp.status_code == 404
        error = resp.json()["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == "not_found"

    def test_patch_validation(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/metric-types", json={
            "name": "Before Patch", "unit": "bpm", "data_type": "number",
        })
        item_id = resp.json()["id"]

        resp = authenticated_client.patch(f"/api/v1/metric-types/{item_id}", json={"name": "After Patch"})
        assert resp.status_code == 200

    def test_delete_not_found(self, authenticated_client: TestClient):
        resp = authenticated_client.delete("/api/v1/metric-types/nonexistent-id")
        assert resp.status_code == 404

    def test_create_requires_auth(self, client: TestClient):
        resp = client.post("/api/v1/metric-types", json={"name": "X", "unit": "kg", "data_type": "number"})
        assert resp.status_code == 401
