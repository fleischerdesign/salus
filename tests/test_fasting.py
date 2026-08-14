import uuid

from starlette.testclient import TestClient


def _push_cmd(client: TestClient, command: str, payload: dict) -> dict:
    resp = client.post(
        "/api/v1/sync/push",
        json={"operations": [{"type": "command", "command": command, "payload": payload}]},
    )
    assert resp.status_code == 200
    return resp.json()["results"][0]


def _fasting_measurements(client: TestClient) -> list[dict]:
    resp = client.get("/api/v1/measurements")
    assert resp.status_code == 200
    return [m for m in resp.json() if m.get("source") == "fasting"]


class TestStartFastingSession:
    def test_start_creates_active_session(self, authenticated_client: TestClient):
        session_id = str(uuid.uuid4())
        result = _push_cmd(authenticated_client, "start_fasting_session", {
            "id": session_id,
            "target_hours": 18.0,
            "fasting_type": "intermittent",
        })
        assert result["status"] == "created"
        assert result["id"] == session_id
        assert result["record"]["ended_at"] is None
        assert result["record"]["target_hours"] == 18.0

    def test_start_returns_existing_active_session(self, authenticated_client: TestClient):
        first = _push_cmd(authenticated_client, "start_fasting_session", {"target_hours": 16.0})
        second = _push_cmd(authenticated_client, "start_fasting_session", {"target_hours": 20.0})
        assert second["id"] == first["id"]
        assert second["record"]["target_hours"] == 16.0


class TestEndFastingSession:
    def test_end_computes_hours_and_writes_measurement(self, authenticated_client: TestClient):
        session_id = str(uuid.uuid4())
        _push_cmd(authenticated_client, "start_fasting_session", {
            "id": session_id,
            "started_at": "2026-08-14T06:00:00",
        })
        ended = "2026-08-15T00:00:00"

        result = _push_cmd(authenticated_client, "end_fasting_session", {
            "session_id": session_id,
            "ended_at": ended,
        })
        assert result["status"] == "updated"
        assert result["record"]["ended_at"] is not None

        measurements = _fasting_measurements(authenticated_client)
        assert len(measurements) == 1
        assert measurements[0]["metric_code"] == "fasting_hours"
        assert measurements[0]["value_numeric"] == 18.0
        assert measurements[0]["external_id"] == session_id

    def test_end_without_ended_at_uses_now(self, authenticated_client: TestClient):
        session_id = str(uuid.uuid4())
        _push_cmd(authenticated_client, "start_fasting_session", {"id": session_id})
        result = _push_cmd(authenticated_client, "end_fasting_session", {"session_id": session_id})
        assert result["status"] == "updated"
        assert result["record"]["ended_at"] is not None

    def test_end_unknown_session(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "end_fasting_session", {"session_id": str(uuid.uuid4())})
        assert result["status"] == "not_found"


class TestCancelFastingSession:
    def test_cancel_active_session(self, authenticated_client: TestClient):
        session_id = str(uuid.uuid4())
        _push_cmd(authenticated_client, "start_fasting_session", {"id": session_id})
        result = _push_cmd(authenticated_client, "cancel_fasting_session", {"session_id": session_id})
        assert result["status"] == "deleted"
        assert _fasting_measurements(authenticated_client) == []

    def test_cancel_completed_session_rejected(self, authenticated_client: TestClient):
        session_id = str(uuid.uuid4())
        _push_cmd(authenticated_client, "start_fasting_session", {"id": session_id})
        _push_cmd(authenticated_client, "end_fasting_session", {"session_id": session_id})
        result = _push_cmd(authenticated_client, "cancel_fasting_session", {"session_id": session_id})
        assert result["status"] == "error"


class TestDeleteFastingSession:
    def test_delete_removes_measurement(self, authenticated_client: TestClient):
        session_id = str(uuid.uuid4())
        _push_cmd(authenticated_client, "start_fasting_session", {"id": session_id})
        _push_cmd(authenticated_client, "end_fasting_session", {"session_id": session_id})
        assert len(_fasting_measurements(authenticated_client)) == 1

        result = _push_cmd(authenticated_client, "delete_fasting_session", {"session_id": session_id})
        assert result["status"] == "deleted"
        assert _fasting_measurements(authenticated_client) == []

    def test_delete_unknown_session(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "delete_fasting_session", {"session_id": str(uuid.uuid4())})
        assert result["status"] == "deleted"
