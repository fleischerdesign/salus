import uuid
from starlette.testclient import TestClient


def _push(client: TestClient, op: dict) -> dict:
    resp = client.post("/api/v1/sync/push", json={"operations": [op]})
    assert resp.status_code == 200
    result = resp.json()["results"][0]
    return result


def _push_cmd(client: TestClient, command: str, payload: dict) -> dict:
    result = _push(client, {"type": "command", "command": command, "payload": payload})
    return result


class TestStartWorkoutHandler:
    def test_start_workout_creates_session(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "create", "entity": "workout_plan", "data": {"name": "Test Plan", "position": 0}}]
        })
        plan_id = resp.json()["results"][0]["id"]

        result = _push_cmd(authenticated_client, "start_workout", {"plan_id": plan_id})
        assert result["status"] == "created"
        assert result["record"]["plan_id"] == plan_id
        assert result["record"]["started_at"] is not None
        assert result["record"]["completed_at"] is None
        assert result["id"] is not None

    def test_start_workout_returns_existing_active_session(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "create", "entity": "workout_plan", "data": {"name": "Plan", "position": 0}}]
        })
        plan_id = resp.json()["results"][0]["id"]

        first = _push_cmd(authenticated_client, "start_workout", {"plan_id": plan_id})
        second = _push_cmd(authenticated_client, "start_workout", {"plan_id": plan_id})
        assert second["status"] == "created"
        assert second["id"] == first["id"]

    def test_start_workout_without_plan(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "start_workout", {})
        assert result["status"] == "created"
        assert result["record"]["recovery_score"] is None

    def test_start_workout_with_client_id(self, authenticated_client: TestClient):
        session_id = str(uuid.uuid4())
        result = _push_cmd(authenticated_client, "start_workout", {
            "plan_id": None, "id": session_id,
        })
        assert result["status"] == "created"
        assert result["id"] == session_id


class TestCompleteWorkoutHandler:
    def test_complete_workout(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "create", "entity": "workout_plan", "data": {"name": "Plan", "position": 0}}]
        })
        plan_id = resp.json()["results"][0]["id"]
        start = _push_cmd(authenticated_client, "start_workout", {"plan_id": plan_id})
        session_id = start["id"]

        result = _push_cmd(authenticated_client, "complete_workout", {"session_id": session_id, "notes": "Great session"})
        assert result["status"] == "updated"
        assert result["record"]["completed_at"] is not None
        assert result["record"]["notes"] == "Great session"

    def test_complete_workout_active_session(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "create", "entity": "workout_plan", "data": {"name": "Plan", "position": 0}}]
        })
        plan_id = resp.json()["results"][0]["id"]
        _push_cmd(authenticated_client, "start_workout", {"plan_id": plan_id})

        result = _push_cmd(authenticated_client, "complete_workout", {"session_id": "active"})
        assert result["status"] == "updated"

    def test_complete_workout_not_found(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "complete_workout", {"session_id": str(uuid.uuid4())})
        assert result["status"] == "not_found"

    def test_complete_workout_missing_session_id(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "complete_workout", {})
        assert result["status"] == "error"
        assert "session_id" in result["message"]


class TestLogSetHandler:
    def test_log_set(self, authenticated_client: TestClient):
        plan_resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "create", "entity": "workout_plan", "data": {"name": "Plan", "position": 0}}]
        })
        plan_id = plan_resp.json()["results"][0]["id"]
        exercise_resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "create", "entity": "exercise", "data": {"name": "Bench Press", "primary_muscles": "chest"}}]
        })
        exercise_id = exercise_resp.json()["results"][0]["id"]
        session = _push_cmd(authenticated_client, "start_workout", {"plan_id": plan_id})
        session_id = session["id"]

        result = _push_cmd(authenticated_client, "log_set", {
            "session_id": session_id,
            "exercise_id": exercise_id,
            "set_number": 1,
            "weight": 100.0,
            "reps": 5,
            "rpe": 8.0,
        })
        assert result["status"] == "created"
        assert result["record"]["weight"] == 100.0
        assert result["record"]["reps"] == 5

    def test_log_set_with_active_session(self, authenticated_client: TestClient):
        plan_resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "create", "entity": "workout_plan", "data": {"name": "Plan", "position": 0}}]
        })
        plan_id = plan_resp.json()["results"][0]["id"]
        exercise_resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "create", "entity": "exercise", "data": {"name": "Squat", "primary_muscles": "quadriceps"}}]
        })
        exercise_id = exercise_resp.json()["results"][0]["id"]
        _push_cmd(authenticated_client, "start_workout", {"plan_id": plan_id})

        result = _push_cmd(authenticated_client, "log_set", {
            "session_id": "active",
            "exercise_id": exercise_id,
            "set_number": 1,
            "weight": 80,
            "reps": 10,
        })
        assert result["status"] == "created"

    def test_log_set_not_found(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "log_set", {
            "session_id": str(uuid.uuid4()),
            "exercise_id": str(uuid.uuid4()),
            "set_number": 1,
            "weight": 50,
            "reps": 3,
        })
        assert result["status"] == "not_found"


class TestDeleteLogSetHandler:
    def test_delete_log_set(self, authenticated_client: TestClient):
        plan_resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "create", "entity": "workout_plan", "data": {"name": "Plan", "position": 0}}]
        })
        plan_id = plan_resp.json()["results"][0]["id"]
        exercise_resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "create", "entity": "exercise", "data": {"name": "Deadlift", "primary_muscles": "back"}}]
        })
        exercise_id = exercise_resp.json()["results"][0]["id"]
        session = _push_cmd(authenticated_client, "start_workout", {"plan_id": plan_id})
        entry = _push_cmd(authenticated_client, "log_set", {
            "session_id": session["id"], "exercise_id": exercise_id, "set_number": 1, "weight": 100, "reps": 5,
        })
        entry_id = entry["id"]

        result = _push_cmd(authenticated_client, "delete_log_set", {"id": entry_id})
        assert result["status"] == "deleted"
        assert result["id"] == entry_id

    def test_delete_log_set_missing_id(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "delete_log_set", {})
        assert result["status"] == "error"


class TestCreateExerciseHandler:
    def test_create_exercise(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "create_exercise", {
            "name": "Pull-up", "equipment": "bodyweight", "primary_muscles": "back,biceps",
        })
        assert result["status"] == "created"
        assert result["record"]["name"] == "Pull-up"
        assert result["record"]["equipment"] == "bodyweight"

    def test_create_exercise_duplicate_name(self, authenticated_client: TestClient):
        _push_cmd(authenticated_client, "create_exercise", {"name": "Unique Exercise", "primary_muscles": "chest"})
        result = _push_cmd(authenticated_client, "create_exercise", {"name": "Unique Exercise", "primary_muscles": "chest"})
        assert result["status"] == "error"
        assert "already exists" in result["message"]


class TestDeleteExerciseHandler:
    def test_delete_exercise(self, authenticated_client: TestClient):
        created = _push_cmd(authenticated_client, "create_exercise", {"name": "To Delete", "primary_muscles": "chest"})
        result = _push_cmd(authenticated_client, "delete_exercise", {"id": created["id"]})
        assert result["status"] == "deleted"

    def test_delete_exercise_not_found(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "delete_exercise", {"id": str(uuid.uuid4())})
        assert result["status"] == "deleted"


class TestCreatePlanHandler:
    def test_create_plan(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "create_plan", {
            "name": "Push Day", "description": "Chest focus", "autoreg_mode": "advisory",
        })
        assert result["status"] == "created"
        assert result["record"]["name"] == "Push Day"
        assert result["record"]["autoreg_mode"] == "advisory"

    def test_create_plan_with_exercises(self, authenticated_client: TestClient):
        ex = _push_cmd(authenticated_client, "create_exercise", {"name": "Bench", "primary_muscles": "chest"})
        result = _push_cmd(authenticated_client, "create_plan", {
            "name": "Push Day", "exercises": [{"exercise_id": ex["id"], "sequence": 0, "target_sets": 3, "target_reps": 8}],
        })
        assert result["status"] == "created"

    def test_create_plan_missing_name(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "create_plan", {})
        assert result["status"] == "error"
        assert "name" in result["message"]


class TestDeletePlanHandler:
    def test_delete_plan(self, authenticated_client: TestClient):
        created = _push_cmd(authenticated_client, "create_plan", {"name": "To Delete"})
        result = _push_cmd(authenticated_client, "delete_plan", {"id": created["id"]})
        assert result["status"] == "deleted"


class TestGoalCommands:
    def test_create_goal(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "create_goal", {
            "metric_code": "steps",
            "target_value": 100.0,
            "direction": "increase",
            "frequency": "daily",
        })
        assert result["status"] == "created"

    def test_delete_goal(self, authenticated_client: TestClient):
        created = _push_cmd(authenticated_client, "create_goal", {
            "metric_code": "steps",
            "target_value": 200.0,
            "direction": "decrease",
            "frequency": "weekly",
        })
        result = _push_cmd(authenticated_client, "delete_goal", {"id": created["id"]})
        assert result["status"] == "deleted"

    def test_delete_goal_not_found(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "delete_goal", {"id": str(uuid.uuid4())})
        assert result["status"] == "not_found"


class TestAccountCommands:
    def test_change_password_success(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "change_password", {
            "current_password": "secret123",
            "new_password": "newsecret456",
        })
        assert result["status"] == "updated"

    def test_change_password_wrong_current(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "change_password", {
            "current_password": "wrongpass",
            "new_password": "newsecret456",
        })
        assert result["status"] == "error"
        assert "incorrect" in result["message"].lower()

    def test_update_profile(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "update_profile", {
            "display_name": "Alice Updated", "theme": "dark", "locale": "de",
        })
        assert result["status"] == "updated"
        assert result["record"]["display_name"] == "Alice Updated"
        assert result["record"]["theme"] == "dark"

    def test_create_and_revoke_token(self, authenticated_client: TestClient):
        created = _push_cmd(authenticated_client, "create_token", {
            "label": "Test Token", "scopes": "entries:read",
        })
        assert created["status"] == "created"
        assert created["record"]["plaintext"] is not None
        assert created["record"]["label"] == "Test Token"

        result = _push_cmd(authenticated_client, "revoke_token", {"id": created["id"]})
        assert result["status"] == "updated"

    def test_dismiss_onboarding(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "dismiss_onboarding", {})
        assert result["status"] == "updated"


class TestNotificationCommands:
    def test_mark_notification_read(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "mark_notification_read", {"id": str(uuid.uuid4())})
        assert result["status"] in ("updated", "not_found")

    def test_mark_all_notifications_read(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "mark_all_notifications_read", {})
        assert result["status"] == "updated"


class TestCircadianCommand:
    def test_save_circadian_profile(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "save_circadian_profile", {
            "latitude": 52.52, "longitude": 13.405,
            "timezone_offset_hours": 2,
            "configured_chronotype": "bear",
        })
        assert result["status"] in ("created", "updated")


class TestCommandSyncVersioning:
    def test_command_requires_sync_version(self, client: TestClient):
        resp = client.post("/api/v1/auth/register", json={
            "username": "cmd_user", "password": "cmd_secret",
            "email": "cmd@example.com", "display_name": "Cmd",
        })
        token = resp.json()["token"]

        resp = client.post(
            "/api/v1/sync/push",
            json={"operations": [{"type": "command", "command": "start_workout", "payload": {}}]},
            headers={"Authorization": f"Bearer {token}", "X-Salus-Sync-Version": "999"},
        )
        assert resp.status_code == 400


class TestCommandBatchOrdering:
    def test_crud_before_command(self, authenticated_client: TestClient):
        plan_created = _push(authenticated_client, {
            "type": "create", "entity": "workout_plan",
            "data": {"name": "Batch Plan", "position": 0},
        })
        plan_id = plan_created["id"]

        # Batch: create plan, then start workout in same push
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [
            {"type": "create", "entity": "exercise", "data": {"name": "OHP", "primary_muscles": "shoulders"}},
            {"type": "command", "command": "start_workout", "payload": {"plan_id": plan_id}},
        ]})
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert results[0]["status"] == "created"
        assert results[1]["status"] == "created"

    def test_command_then_crud(self, authenticated_client: TestClient):
        plan_created = _push(authenticated_client, {
            "type": "create", "entity": "workout_plan",
            "data": {"name": "Batch Plan 2", "position": 0},
        })
        plan_id = plan_created["id"]

        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [
            {"type": "command", "command": "start_workout", "payload": {"plan_id": plan_id}},
            {"type": "create", "entity": "exercise", "data": {"name": "Row", "primary_muscles": "back"}},
        ]})
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert results[0]["status"] == "created"
        assert results[1]["status"] == "created"


class TestCommandErrorPropagation:
    def test_unknown_command(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "nonexistent_command", {})
        assert result["status"] == "error"
        assert "Unknown command" in result["message"]

    def test_command_without_command_field(self, authenticated_client: TestClient):
        resp = authenticated_client.post("/api/v1/sync/push", json={
            "operations": [{"type": "command", "payload": {}}]
        })
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "error"
        assert "command field" in result["message"].lower()


class TestCommandCrossUserSecurity:
    def test_cannot_complete_others_session(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "complete_workout", {"session_id": str(uuid.uuid4())})
        assert result["status"] == "not_found"
