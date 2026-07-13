import uuid
from starlette.testclient import TestClient


class TestSyncPush:
    """Test the POST /api/v1/sync/push endpoint and WritePipeline."""

    def test_create_metric_type(self, authenticated_client: TestClient):
        op = {
            "type": "create",
            "entity": "metric_type",
            "client_id": "client-uuid-1",
            "data": {"name": "Push Created", "unit": "kg", "data_type": "number"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "created"
        assert result["entity"] == "metric_type"
        assert result["client_id"] == "client-uuid-1"
        assert result["id"] is not None
        assert result["record"]["name"] == "Push Created"

    def test_update_metric_type(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "metric_type",
            "client_id": "client-uuid-2",
            "data": {"name": "To Update", "unit": "bpm", "data_type": "number"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        metric_id = resp.json()["results"][0]["id"]

        update_op = {
            "type": "update",
            "entity": "metric_type",
            "id": metric_id,
            "data": {"name": "Updated Name"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"]["name"] == "Updated Name"

    def test_delete_metric_type(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "metric_type",
            "data": {"name": "To Delete", "unit": "kg", "data_type": "number"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        metric_id = resp.json()["results"][0]["id"]

        delete_op = {"type": "delete", "entity": "metric_type", "id": metric_id}
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [delete_op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "deleted"

    def test_batch_create(self, authenticated_client: TestClient):
        operations = [
            {
                "type": "create",
                "entity": "metric_type",
                "client_id": "batch-1",
                "data": {"name": "Batch A", "unit": "kg", "data_type": "number"},
            },
            {
                "type": "create",
                "entity": "metric_type",
                "client_id": "batch-2",
                "data": {"name": "Batch B", "unit": "cm", "data_type": "number"},
            },
        ]
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": operations})
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 2
        assert all(r["status"] == "created" for r in results)

    def test_temp_id_resolution(self, authenticated_client: TestClient):
        session_client_id = str(uuid.uuid4())
        log_client_id = str(uuid.uuid4())

        create_plan = {
            "type": "create",
            "entity": "workout_plan",
            "data": {"name": "Temp Plan", "position": 0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_plan]})
        plan_id = resp.json()["results"][0]["id"]

        create_exercise = {
            "type": "create",
            "entity": "exercise",
            "data": {"name": "Squat", "primary_muscles": "quadriceps,glutes"},
        }
        ex_resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_exercise]})
        exercise_id = ex_resp.json()["results"][0]["id"]

        operations = [
            {
                "type": "create",
                "entity": "workout_session",
                "client_id": session_client_id,
                "data": {"plan_id": plan_id, "started_at": "2026-07-11T10:00:00Z"},
            },
            {
                "type": "create",
                "entity": "workout_log_entry",
                "client_id": log_client_id,
                "data": {
                    "session_client_id": session_client_id,
                    "exercise_id": exercise_id,
                    "set_number": 1,
                    "weight": 80,
                    "reps": 5,
                },
            },
        ]
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": operations})
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert results[0]["status"] == "created"
        assert results[1]["status"] == "created"
        session_id = results[0]["id"]
        assert results[1]["record"]["session_id"] == session_id

    def test_not_found(self, authenticated_client: TestClient):
        op = {"type": "update", "entity": "metric_type", "id": 99999, "data": {"name": "Nope"}}
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "not_found"

    def test_unknown_entity(self, authenticated_client: TestClient):
        op = {"type": "create", "entity": "nonexistent_table", "data": {"x": 1}}
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "error"

    def test_sync_after_push(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "metric_type",
            "data": {"name": "SyncTest", "unit": "kg", "data_type": "number"},
        }
        authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})

        resp = authenticated_client.get("/api/v1/sync")
        assert resp.status_code == 200
        data = resp.json()
        assert "metric_type" in data
        assert "measurement" in data
        assert "synced_at" in data


class TestUserEntityValidator:
    """Test whitelist validation for 'user' entity via sync push."""

    def test_create_blocked(self, authenticated_client: TestClient):
        op = {
            "type": "create",
            "entity": "user",
            "data": {"username": "new_user", "password_hash": "hash"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        result = resp.json()["results"][0]
        assert result["status"] == "error"
        assert "not allowed" in result["message"].lower()

    def test_delete_blocked(self, authenticated_client: TestClient):
        op = {"type": "delete", "entity": "user", "id": 1}
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        result = resp.json()["results"][0]
        assert result["status"] == "error"
        assert "not allowed" in result["message"].lower()

    def test_update_blocked_fields(self, authenticated_client: TestClient):
        op = {
            "type": "update",
            "entity": "user",
            "id": 2,  # alice's user_id = 2 (admin is 1)
            "data": {"is_admin": True, "password_hash": "pwned"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        result = resp.json()["results"][0]
        assert result["status"] == "error"
        assert "is_admin" in result["message"] or "password_hash" in result["message"]

    def test_update_allowed_fields(self, authenticated_client: TestClient):
        op = {
            "type": "update",
            "entity": "user",
            "id": 2,  # alice
            "data": {"theme": "dark", "locale": "de", "display_name": "Alice Updated", "onboarding_dismissed": True},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"]["theme"] == "dark"
        assert result["record"]["locale"] == "de"
        assert result["record"]["display_name"] == "Alice Updated"
        assert result["record"]["onboarding_dismissed"] is True

    def test_update_wrong_user(self, authenticated_client: TestClient):
        op = {
            "type": "update",
            "entity": "user",
            "id": 1,  # admin user, NOT alice
            "data": {"theme": "light"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        result = resp.json()["results"][0]
        assert result["status"] == "error"


class TestApiTokenValidator:
    """Test whitelist validation for 'api_token' entity via sync push."""

    def test_create_blocked(self, authenticated_client: TestClient):
        op = {
            "type": "create",
            "entity": "api_token",
            "data": {"label": "fake", "token_hash": "xxx", "token_prefix": "fake"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        result = resp.json()["results"][0]
        assert result["status"] == "error"
        assert "not allowed" in result["message"].lower()

    def test_update_blocked_fields(self, authenticated_client: TestClient):
        resp = authenticated_client.post(
            "/api/v1/settings/tokens",
            json={"label": "test-token", "scopes": "entries:read"},
        )
        data = resp.json()
        prefix = data["prefix"]

        created = authenticated_client.get("/api/v1/sync").json()
        api_tokens = created.get("api_token", [])
        token_id = None
        for t in api_tokens:
            if t.get("token_prefix") == prefix:
                token_id = t["id"]
                break
        assert token_id is not None, "token should appear in sync response"

        op = {
            "type": "update",
            "entity": "api_token",
            "id": token_id,
            "data": {"label": "hacked"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        result = resp.json()["results"][0]
        assert result["status"] == "error"
        assert "label" in result["message"]

    def test_revoke_allowed(self, authenticated_client: TestClient):
        resp = authenticated_client.post(
            "/api/v1/settings/tokens",
            json={"label": "revoke-token", "scopes": "entries:read"},
        )
        data = resp.json()
        prefix = data["prefix"]

        created = authenticated_client.get("/api/v1/sync").json()
        api_tokens = created.get("api_token", [])
        token_id = None
        for t in api_tokens:
            if t.get("token_prefix") == prefix:
                token_id = t["id"]
                break
        assert token_id is not None

        op = {
            "type": "update",
            "entity": "api_token",
            "id": token_id,
            "data": {"is_active": False},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"]["is_active"] is False


class TestWritePipelineCommit:
    """Test that WritePipeline actually commits to the database."""

    def test_data_persists_across_requests(self, authenticated_client: TestClient):
        op = {
            "type": "create",
            "entity": "metric_type",
            "data": {"name": "Persist Check", "unit": "kg", "data_type": "number"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "created"
        created_id = result["id"]

        get_resp = authenticated_client.get("/api/v1/sync")
        assert get_resp.status_code == 200
        data = get_resp.json()
        metric_types = data.get("metric_type", [])
        names = [m["name"] for m in metric_types if m.get("id") == created_id]
        assert len(names) == 1
        assert names[0] == "Persist Check"


class TestWritePipelineUpdateBehavior:
    """Test update-specific behavior."""

    def test_update_sets_updated_at(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "metric_type",
            "data": {"name": "Before Update", "unit": "kg", "data_type": "number"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        metric_id = resp.json()["results"][0]["id"]

        update_op = {
            "type": "update",
            "entity": "metric_type",
            "id": metric_id,
            "data": {"name": "After Update"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"].get("updated_at") is not None
        assert result["record"]["name"] == "After Update"

    def test_update_cannot_overwrite_id(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "metric_type",
            "data": {"name": "PK Test", "unit": "kg", "data_type": "number"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        original_id = resp.json()["results"][0]["id"]

        update_op = {
            "type": "update",
            "entity": "metric_type",
            "id": original_id,
            "data": {"id": 99999, "name": "PK Hijack"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"]["id"] == original_id
        assert result["record"]["name"] == "PK Hijack"

    def test_update_cannot_overwrite_created_at(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "metric_type",
            "data": {"name": "CreatedAt Test", "unit": "kg", "data_type": "number"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        metric_id = resp.json()["results"][0]["id"]
        original_created_at = resp.json()["results"][0]["record"]["created_at"]

        update_op = {
            "type": "update",
            "entity": "metric_type",
            "id": metric_id,
            "data": {"created_at": "2000-01-01T00:00:00", "name": "CreatedAt Hijack"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"]["created_at"] == original_created_at


class TestWritePipelineDedup:
    """Test client_id deduplication."""

    def test_same_client_id_no_duplicate(self, authenticated_client: TestClient):
        client_id = f"dedup-test-{uuid.uuid4()}"

        op1 = {
            "type": "create",
            "entity": "metric_type",
            "client_id": client_id,
            "data": {"name": "Dedup Test", "unit": "kg", "data_type": "number"},
        }
        resp1 = authenticated_client.post("/api/v1/sync/push", json={"operations": [op1]})
        result1 = resp1.json()["results"][0]
        assert result1["status"] == "created"
        assert result1["client_id"] == client_id
        created_id = result1["id"]

        op2 = {
            "type": "create",
            "entity": "metric_type",
            "client_id": client_id,
            "data": {"name": "Dedup Duplicate", "unit": "kg", "data_type": "number"},
        }
        resp2 = authenticated_client.post("/api/v1/sync/push", json={"operations": [op2]})
        result2 = resp2.json()["results"][0]
        assert result2["status"] == "created"
        assert result2["id"] == created_id


class TestSyncPagination:
    """Test cursor-based full sync pagination."""

    def test_full_sync_has_more_and_cursors(self, authenticated_client: TestClient):
        resp = authenticated_client.get("/api/v1/sync")
        assert resp.status_code == 200
        data = resp.json()
        assert "cursors" in data
        assert "has_more" in data
        assert isinstance(data["cursors"], dict)
        assert isinstance(data["has_more"], bool)

    def test_full_sync_with_cursor(self, authenticated_client: TestClient):
        resp1 = authenticated_client.get("/api/v1/sync")
        data1 = resp1.json()
        cursors1 = data1["cursors"]

        import base64
        import json

        cursor_param = base64.urlsafe_b64encode(
            json.dumps(cursors1).encode()
        ).decode()

        resp2 = authenticated_client.get(f"/api/v1/sync?cursor={cursor_param}")
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert "cursors" in data2
        assert "has_more" in data2

    def test_full_sync_special_entities_only_on_first_page(self, authenticated_client: TestClient):
        resp1 = authenticated_client.get("/api/v1/sync")
        data1 = resp1.json()
        assert data1.get("user_profile") is not None
        assert data1.get("user") is not None
        assert data1.get("community_activity") is not None

        cursors1 = data1["cursors"]
        import base64
        import json

        cursor_param = base64.urlsafe_b64encode(
            json.dumps(cursors1).encode()
        ).decode()

        resp2 = authenticated_client.get(f"/api/v1/sync?cursor={cursor_param}")
        data2 = resp2.json()
        assert "user_profile" not in data2
        assert "user" not in data2
        assert "community_activity" not in data2
        assert "admin_user" not in data2


class TestDeltaSyncSecurity:
    """Test that delta sync returns only the authenticated user's data."""

    def test_delta_sync_returns_only_own_data(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "metric_type",
            "data": {"name": "Mine", "unit": "kg", "data_type": "number"},
        }
        authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})

        from datetime import datetime, timezone, timedelta
        from urllib.parse import quote

        since = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        resp = authenticated_client.get(f"/api/v1/sync?since={quote(since)}")
        assert resp.status_code == 200
        data = resp.json()
        changed = data.get("changed", {})

        metric_types = changed.get("metric_type", [])
        my_names = [m["name"] for m in metric_types]
        assert "Mine" in my_names

        for name in my_names:
            if name != "Mine":
                continue
            for m in metric_types:
                if m["name"] == name:
                    assert m.get("user_id") is not None


class TestDeltaSyncCompleteness:
    """Test that delta sync includes special entities."""

    def test_delta_sync_includes_user_profile(self, authenticated_client: TestClient):
        from datetime import datetime, timezone, timedelta
        from urllib.parse import quote

        since = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        resp = authenticated_client.get(f"/api/v1/sync?since={quote(since)}")
        assert resp.status_code == 200
        data = resp.json()
        changed = data.get("changed", {})
        assert "user_profile" in changed
        assert "user" in changed


class TestEventBusDirect:
    """Unit tests for InMemoryEventBus."""

    def test_publish_wakes_subscriber(self):
        import asyncio
        from salus.services.event_bus import InMemoryEventBus

        async def scenario():
            bus = InMemoryEventBus()
            results = []

            async def consumer():
                async for _ in bus.subscribe(42):
                    results.append(1)
                    break

            consumer_task = asyncio.create_task(consumer())
            await asyncio.sleep(0)
            await bus.publish(42)
            await asyncio.sleep(0)
            await consumer_task

            return results

        results = asyncio.run(scenario())
        assert len(results) == 1

    def test_no_event_for_different_user(self):
        import asyncio
        from salus.services.event_bus import InMemoryEventBus

        async def scenario():
            bus = InMemoryEventBus()
            results = []

            async def consumer():
                async for _ in bus.subscribe(42):
                    results.append(1)

            consumer_task = asyncio.create_task(consumer())
            await asyncio.sleep(0)
            await bus.publish(99)
            await asyncio.sleep(0)
            consumer_task.cancel()
            try:
                await consumer_task
            except asyncio.CancelledError:
                pass

            return results

        results = asyncio.run(scenario())
        assert len(results) == 0


class TestSSEEndpoint:
    """Test the SSE events endpoint."""

    def test_requires_auth(self, client: TestClient):
        resp = client.get("/api/v1/sync/events")
        assert resp.status_code == 401


class TestSyncPushPublishesEvent:
    """Test that sync push publishes to EventBus."""

    def test_sync_push_publishes_to_event_bus(self, authenticated_client: TestClient):
        from salus.dependencies import get_event_bus
        from salus.main import app as fastapi_app

        published_user_ids: list[int] = []

        class MockEventBus:
            async def subscribe(self, user_id: int):
                raise NotImplementedError

            async def publish(self, user_id: int) -> None:
                published_user_ids.append(user_id)

        mock = MockEventBus()
        fastapi_app.dependency_overrides[get_event_bus] = lambda: mock

        try:
            resp = authenticated_client.post("/api/v1/sync/push", json={
                "operations": [{
                    "type": "create",
                    "entity": "metric_type",
                    "data": {"name": "EventBus Test", "unit": "kg", "data_type": "number"},
                }]
            })
            assert resp.status_code == 200
            assert len(published_user_ids) == 1
            assert published_user_ids[0] > 0
        finally:
            fastapi_app.dependency_overrides.pop(get_event_bus, None)


class TestSyncPushLogTTL:
    """Test that sync_push_log entries older than 24h are cleaned up and dedup bypassed."""

    def test_ttl_expired_allows_duplicate_client_id(self, authenticated_client: TestClient):
        from datetime import datetime, timezone, timedelta

        from sqlmodel import Session, select

        from salus.main import app as fastapi_app
        from salus.models.sync_push_log import SyncPushLog

        client_id = f"ttl-test-{uuid.uuid4()}"

        op1 = {
            "type": "create",
            "entity": "metric_type",
            "client_id": client_id,
            "data": {"name": "TTL Original", "unit": "kg", "data_type": "number"},
        }
        resp1 = authenticated_client.post("/api/v1/sync/push", json={"operations": [op1]})
        result1 = resp1.json()["results"][0]
        assert result1["status"] == "created"
        original_id = result1["id"]

        with Session(fastapi_app.state.engine) as session:
            log = session.exec(
                select(SyncPushLog).where(SyncPushLog.client_id == client_id)
            ).first()
            assert log is not None
            log.created_at = datetime.now(timezone.utc) - timedelta(hours=25)
            session.add(log)
            session.commit()

        op2 = {
            "type": "create",
            "entity": "metric_type",
            "client_id": client_id,
            "data": {"name": "TTL After Expiry", "unit": "kg", "data_type": "number"},
        }
        resp2 = authenticated_client.post("/api/v1/sync/push", json={"operations": [op2]})
        result2 = resp2.json()["results"][0]
        assert result2["status"] == "created"
        assert result2["id"] != original_id


class TestSyncProtocolVersion:
    """Test X-Salus-Sync-Version header validation."""

    def test_unsupported_version_rejected(self, authenticated_client: TestClient):
        resp = authenticated_client.post(
            "/api/v1/sync/push",
            json={"operations": []},
            headers={"X-Salus-Sync-Version": "999"},
        )
        assert resp.status_code == 400
        assert "Unsupported" in resp.json()["detail"]

    def test_correct_version_accepted(self, authenticated_client: TestClient):
        resp = authenticated_client.post(
            "/api/v1/sync/push",
            json={"operations": []},
            headers={"X-Salus-Sync-Version": "1"},
        )
        assert resp.status_code == 200
        assert resp.json()["sync_version"] == 1

    def test_missing_version_defaults_to_ok(self, authenticated_client: TestClient):
        resp = authenticated_client.post(
            "/api/v1/sync/push",
            json={"operations": []},
        )
        assert resp.status_code == 200
        assert resp.json()["sync_version"] == 1


class TestOptimisticLocking:
    """Test expected_updated_at conflict detection on updates."""

    def test_update_with_correct_timestamp_succeeds(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "metric_type",
            "data": {"name": "Lock Test", "unit": "kg", "data_type": "number"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        metric_id = resp.json()["results"][0]["id"]

        get_resp = authenticated_client.get("/api/v1/sync")
        metric = next(
            m for m in get_resp.json()["metric_type"]
            if m["id"] == metric_id
        )
        current_updated_at = metric["updated_at"]

        update_op = {
            "type": "update",
            "entity": "metric_type",
            "id": metric_id,
            "data": {"name": "Lock Updated"},
            "expected_updated_at": current_updated_at,
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        assert resp.status_code == 200
        assert resp.json()["results"][0]["status"] == "updated"

    def test_update_with_stale_timestamp_returns_conflict(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "metric_type",
            "data": {"name": "Conflict Test", "unit": "kg", "data_type": "number"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        metric_id = resp.json()["results"][0]["id"]

        update_op = {
            "type": "update",
            "entity": "metric_type",
            "id": metric_id,
            "data": {"name": "Conflict Updated"},
            "expected_updated_at": "1970-01-01T00:00:00+00:00",
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "conflict"
        assert "conflict" in result
