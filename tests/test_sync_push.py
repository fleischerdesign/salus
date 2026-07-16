import uuid
from starlette.testclient import TestClient


class TestSyncPush:
    """Test the POST /api/v1/sync/push endpoint and WritePipeline."""

    def test_create_goal_via_sync_push(self, authenticated_client: TestClient):
        op = {
            "type": "create",
            "entity": "goal",
            "client_id": "client-uuid-1",
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "created"
        assert result["entity"] == "goal"
        assert result["client_id"] == "client-uuid-1"
        assert result["id"] is not None
        assert result["record"]["metric_code"] == "steps"

    def test_update_goal(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "goal",
            "client_id": "client-uuid-2",
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        goal_id = resp.json()["results"][0]["id"]

        update_op = {
            "type": "update",
            "entity": "goal",
            "id": goal_id,
            "data": {"target_value": 200.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"]["target_value"] == 200.0

    def test_delete_goal(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "goal",
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        goal_id = resp.json()["results"][0]["id"]

        delete_op = {"type": "delete", "entity": "goal", "id": goal_id}
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [delete_op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "deleted"

    def test_batch_create(self, authenticated_client: TestClient):
        operations = [
            {
                "type": "create",
                "entity": "goal",
                "client_id": "batch-1",
                "data": {"metric_code": "steps", "target_value": 100.0},
            },
            {
                "type": "create",
                "entity": "goal",
                "client_id": "batch-2",
                "data": {"metric_code": "water", "target_value": 2000.0},
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
        op = {"type": "update", "entity": "goal", "id": "99999", "data": {"target_value": 999.0}}
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
            "entity": "goal",
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})

        resp = authenticated_client.get("/api/v1/sync")
        assert resp.status_code == 200
        data = resp.json()
        assert "measurement" in data
        assert "goal" in data
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
        resp_acc = authenticated_client.get("/api/v1/settings/account")
        alice_id = resp_acc.json()["user"]["id"]
        op = {"type": "delete", "entity": "user", "id": alice_id}
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        result = resp.json()["results"][0]
        assert result["status"] == "error"
        assert "not allowed" in result["message"].lower()

    def test_update_blocked_fields(self, authenticated_client: TestClient):
        resp_acc = authenticated_client.get("/api/v1/settings/account")
        alice_id = resp_acc.json()["user"]["id"]
        op = {
            "type": "update",
            "entity": "user",
            "id": alice_id,
            "data": {"is_admin": True, "password_hash": "pwned"},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        result = resp.json()["results"][0]
        assert result["status"] == "error"
        assert "is_admin" in result["message"] or "password_hash" in result["message"]

    def test_update_allowed_fields(self, authenticated_client: TestClient):
        resp_acc = authenticated_client.get("/api/v1/settings/account")
        alice_id = resp_acc.json()["user"]["id"]
        op = {
            "type": "update",
            "entity": "user",
            "id": alice_id,
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
        import uuid
        op = {
            "type": "update",
            "entity": "user",
            "id": str(uuid.uuid4()),  # Some other user ID, NOT alice
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
            "entity": "goal",
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "created"
        created_id = result["id"]

        get_resp = authenticated_client.get("/api/v1/sync")
        assert get_resp.status_code == 200
        data = get_resp.json()
        goals = data.get("goal", [])
        matching = [g for g in goals if g.get("id") == created_id]
        assert len(matching) == 1
        assert matching[0]["metric_code"] == "steps"


class TestWritePipelineUpdateBehavior:
    """Test update-specific behavior."""

    def test_update_sets_updated_at(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "goal",
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        goal_id = resp.json()["results"][0]["id"]

        update_op = {
            "type": "update",
            "entity": "goal",
            "id": goal_id,
            "data": {"target_value": 200.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"].get("updated_at") is not None
        assert result["record"]["target_value"] == 200.0

    def test_update_cannot_overwrite_id(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "goal",
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        original_id = resp.json()["results"][0]["id"]

        update_op = {
            "type": "update",
            "entity": "goal",
            "id": original_id,
            "data": {"id": 99999, "target_value": 300.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"]["id"] == original_id
        assert result["record"]["target_value"] == 300.0

    def test_update_cannot_overwrite_created_at(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "goal",
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        goal_id = resp.json()["results"][0]["id"]
        original_created_at = resp.json()["results"][0]["record"]["created_at"]

        update_op = {
            "type": "update",
            "entity": "goal",
            "id": goal_id,
            "data": {"created_at": "2000-01-01T00:00:00", "target_value": 400.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"]["created_at"] == original_created_at

    def test_update_datetime_coercion(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "workout_session",
            "data": {
                "started_at": "2026-07-14T08:00:00Z",
            },
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        session_id = resp.json()["results"][0]["id"]

        update_op = {
            "type": "update",
            "entity": "workout_session",
            "id": session_id,
            "data": {
                "completed_at": "2026-07-14T08:10:51.212Z",
            },
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        result = resp.json()["results"][0]
        assert result["status"] == "updated"
        assert result["record"]["completed_at"] == "2026-07-14T08:10:51.212000"


class TestWritePipelineDedup:
    """Test client_id deduplication."""

    def test_same_client_id_no_duplicate(self, authenticated_client: TestClient):
        client_id = f"dedup-test-{uuid.uuid4()}"

        op1 = {
            "type": "create",
            "entity": "goal",
            "client_id": client_id,
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        resp1 = authenticated_client.post("/api/v1/sync/push", json={"operations": [op1]})
        result1 = resp1.json()["results"][0]
        assert result1["status"] == "created"
        assert result1["client_id"] == client_id
        created_id = result1["id"]

        op2 = {
            "type": "create",
            "entity": "goal",
            "client_id": client_id,
            "data": {"metric_code": "steps", "target_value": 200.0},
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
            "entity": "goal",
            "data": {"metric_code": "steps", "target_value": 500.0},
        }
        authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})

        from datetime import datetime, timezone, timedelta
        from urllib.parse import quote

        since = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
        resp = authenticated_client.get(f"/api/v1/sync?since={quote(since)}")
        assert resp.status_code == 200
        data = resp.json()
        changed = data.get("changed", {})

        goals = changed.get("goal", [])
        my_targets = [g["target_value"] for g in goals]
        assert 500.0 in my_targets

        for g in goals:
            if g["target_value"] == 500.0:
                assert g.get("user_id") is not None


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
            async def subscribe(self, user_id: str):
                raise NotImplementedError

            async def publish(self, user_id: str) -> None:
                published_user_ids.append(user_id)

        mock = MockEventBus()
        fastapi_app.dependency_overrides[get_event_bus] = lambda: mock

        try:
            resp = authenticated_client.post("/api/v1/sync/push", json={
                "operations": [{
                    "type": "create",
                    "entity": "goal",
                    "data": {"metric_code": "steps", "target_value": 100.0},
                }]
            })
            assert resp.status_code == 200
            assert len(published_user_ids) == 1
            assert len(published_user_ids[0]) > 0
        finally:
            fastapi_app.dependency_overrides.pop(get_event_bus, None)


    def test_command_publishes_to_event_bus(self, authenticated_client: TestClient):
        from salus.dependencies import get_event_bus
        from salus.main import app as fastapi_app

        published_user_ids: list[str] = []

        class MockEventBus:
            async def subscribe(self, user_id: str):
                raise NotImplementedError

            async def publish(self, user_id: str) -> None:
                published_user_ids.append(user_id)

        mock = MockEventBus()
        fastapi_app.dependency_overrides[get_event_bus] = lambda: mock

        try:
            # Create a plan first (needed for start_workout)
            plan_resp = authenticated_client.post("/api/v1/sync/push", json={
                "operations": [{
                    "type": "create",
                    "entity": "workout_plan",
                    "data": {"name": "EventBus Plan", "position": 0},
                }]
            })
            plan_id = plan_resp.json()["results"][0]["id"]
            expected_min_publishes = len(published_user_ids) + 1

            resp = authenticated_client.post("/api/v1/sync/push", json={
                "operations": [{
                    "type": "command",
                    "command": "start_workout",
                    "payload": {"plan_id": plan_id},
                }]
            })
            assert resp.status_code == 200
            assert len(published_user_ids) >= expected_min_publishes
            assert len(published_user_ids[-1]) > 0
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
            "entity": "goal",
            "client_id": client_id,
            "data": {"metric_code": "steps", "target_value": 100.0},
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
            "entity": "goal",
            "client_id": client_id,
            "data": {"metric_code": "steps", "target_value": 200.0},
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
            "entity": "goal",
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        goal_id = resp.json()["results"][0]["id"]

        get_resp = authenticated_client.get("/api/v1/sync")
        goal = next(
            g for g in get_resp.json()["goal"]
            if g["id"] == goal_id
        )
        current_updated_at = goal["updated_at"]

        update_op = {
            "type": "update",
            "entity": "goal",
            "id": goal_id,
            "data": {"target_value": 200.0},
            "expected_updated_at": current_updated_at,
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        assert resp.status_code == 200
        assert resp.json()["results"][0]["status"] == "updated"

    def test_update_with_stale_timestamp_returns_conflict(self, authenticated_client: TestClient):
        create_op = {
            "type": "create",
            "entity": "goal",
            "data": {"metric_code": "steps", "target_value": 100.0},
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [create_op]})
        goal_id = resp.json()["results"][0]["id"]

        update_op = {
            "type": "update",
            "entity": "goal",
            "id": goal_id,
            "data": {"target_value": 300.0},
            "expected_updated_at": "1970-01-01T00:00:00+00:00",
        }
        resp = authenticated_client.post("/api/v1/sync/push", json={"operations": [update_op]})
        assert resp.status_code == 200
        result = resp.json()["results"][0]
        assert result["status"] == "conflict"
        assert "conflict" in result
