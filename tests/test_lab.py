import uuid

from starlette.testclient import TestClient


def _push_cmd(client: TestClient, command: str, payload: dict) -> dict:
    resp = client.post(
        "/api/v1/sync/push",
        json={"operations": [{"type": "command", "command": command, "payload": payload}]},
    )
    assert resp.status_code == 200
    return resp.json()["results"][0]


def _sync(client: TestClient) -> dict:
    resp = client.get("/api/v1/sync")
    assert resp.status_code == 200
    return resp.json()


def _lab_measurements(client: TestClient) -> list[dict]:
    resp = client.get("/api/v1/measurements")
    assert resp.status_code == 200
    return [m for m in resp.json() if m.get("source") == "lab"]


class TestCreateLabPanel:
    def test_create_panel_with_results(self, authenticated_client: TestClient):
        panel_id = str(uuid.uuid4())
        result_id = str(uuid.uuid4())
        result = _push_cmd(authenticated_client, "create_lab_panel", {
            "id": panel_id,
            "collection_date": "2026-08-14",
            "lab_name": "LabCorp",
            "fasting": True,
            "results": [{"id": result_id, "metric_code": "total_cholesterol", "value": 240.0}],
        })
        assert result["status"] == "created"
        assert result["record"]["lab_name"] == "LabCorp"
        assert result["record"]["fasting"] is True

        data = _sync(authenticated_client)
        assert len(data["lab_panel"]) == 1
        assert data["lab_panel"][0]["id"] == panel_id
        assert data["lab_panel"][0]["collection_date"] == "2026-08-14"
        assert len(data["lab_result"]) == 1

    def test_abnormal_derived_from_reference_high(self, authenticated_client: TestClient):
        _push_cmd(authenticated_client, "create_lab_panel", {
            "results": [{"metric_code": "total_cholesterol", "value": 240.0}],
        })
        results = _sync(authenticated_client)["lab_result"]
        assert results[0]["is_abnormal"] is True

    def test_within_range_is_not_abnormal(self, authenticated_client: TestClient):
        _push_cmd(authenticated_client, "create_lab_panel", {
            "results": [{"metric_code": "total_cholesterol", "value": 180.0}],
        })
        results = _sync(authenticated_client)["lab_result"]
        assert results[0]["is_abnormal"] is False

    def test_explicit_abnormal_overrides_derivation(self, authenticated_client: TestClient):
        _push_cmd(authenticated_client, "create_lab_panel", {
            "results": [{"metric_code": "total_cholesterol", "value": 240.0, "is_abnormal": False}],
        })
        results = _sync(authenticated_client)["lab_result"]
        assert results[0]["is_abnormal"] is False

    def test_low_bound_derivation(self, authenticated_client: TestClient):
        _push_cmd(authenticated_client, "create_lab_panel", {
            "results": [{"metric_code": "hdl_cholesterol", "value": 30.0}],
        })
        results = _sync(authenticated_client)["lab_result"]
        assert results[0]["is_abnormal"] is True

    def test_writes_measurement_bridge(self, authenticated_client: TestClient):
        result_id = str(uuid.uuid4())
        _push_cmd(authenticated_client, "create_lab_panel", {
            "results": [{"id": result_id, "metric_code": "hdl_cholesterol", "value": 55.0}],
        })
        measurements = _lab_measurements(authenticated_client)
        assert len(measurements) == 1
        assert measurements[0]["metric_code"] == "hdl_cholesterol"
        assert measurements[0]["value_numeric"] == 55.0
        assert measurements[0]["external_id"] == result_id


class TestUpdateLabPanel:
    def test_update_replaces_results_and_measurements(self, authenticated_client: TestClient):
        panel_id = str(uuid.uuid4())
        old_result_id = str(uuid.uuid4())
        new_result_id = str(uuid.uuid4())
        _push_cmd(authenticated_client, "create_lab_panel", {
            "id": panel_id,
            "results": [{"id": old_result_id, "metric_code": "hdl_cholesterol", "value": 55.0}],
        })

        result = _push_cmd(authenticated_client, "update_lab_panel", {
            "id": panel_id,
            "lab_name": "Quest",
            "results": [{"id": new_result_id, "metric_code": "ldl_cholesterol", "value": 120.0}],
        })
        assert result["status"] == "updated"
        assert result["record"]["lab_name"] == "Quest"

        data = _sync(authenticated_client)
        assert len(data["lab_result"]) == 1
        assert data["lab_result"][0]["id"] == new_result_id

        measurements = _lab_measurements(authenticated_client)
        assert len(measurements) == 1
        assert measurements[0]["metric_code"] == "ldl_cholesterol"
        assert measurements[0]["external_id"] == new_result_id

    def test_update_without_results_keeps_them(self, authenticated_client: TestClient):
        panel_id = str(uuid.uuid4())
        _push_cmd(authenticated_client, "create_lab_panel", {
            "id": panel_id,
            "results": [{"metric_code": "hdl_cholesterol", "value": 55.0}],
        })
        result = _push_cmd(authenticated_client, "update_lab_panel", {
            "id": panel_id,
            "notes": "rechecked",
        })
        assert result["status"] == "updated"
        data = _sync(authenticated_client)
        assert len(data["lab_result"]) == 1
        assert data["lab_panel"][0]["notes"] == "rechecked"


class TestDeleteLabPanel:
    def test_delete_removes_results_and_measurements(self, authenticated_client: TestClient):
        panel_id = str(uuid.uuid4())
        _push_cmd(authenticated_client, "create_lab_panel", {
            "id": panel_id,
            "results": [{"metric_code": "hdl_cholesterol", "value": 55.0}],
        })
        assert len(_lab_measurements(authenticated_client)) == 1

        result = _push_cmd(authenticated_client, "delete_lab_panel", {"id": panel_id})
        assert result["status"] == "deleted"

        data = _sync(authenticated_client)
        assert len(data["lab_panel"]) == 0
        assert len(data["lab_result"]) == 0
        assert _lab_measurements(authenticated_client) == []

    def test_delete_unknown_panel_is_idempotent(self, authenticated_client: TestClient):
        result = _push_cmd(authenticated_client, "delete_lab_panel", {"id": str(uuid.uuid4())})
        assert result["status"] == "deleted"
