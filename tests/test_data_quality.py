import uuid
from datetime import datetime, timedelta

from starlette.testclient import TestClient


def _push(client: TestClient, operations: list[dict]) -> list[dict]:
    resp = client.post("/api/v1/sync/push", json={"operations": operations})
    assert resp.status_code == 200
    return resp.json()["results"]


def _push_cmd(client: TestClient, command: str, payload: dict) -> dict:
    return _push(client, [{"type": "command", "command": command, "payload": payload}])[0]


def _measurement(
    metric_code: str,
    value: float,
    start_time: str,
    source: str = "manual",
    measurement_id: str | None = None,
) -> dict:
    return {
        "type": "create",
        "entity": "measurement",
        "data": {
            "id": measurement_id or str(uuid.uuid4()),
            "metric_code": metric_code,
            "source_data_type": metric_code,
            "source": source,
            "value_numeric": value,
            "start_time": start_time,
        },
    }


def _flags(client: TestClient) -> list[dict]:
    resp = client.get("/api/v1/sync")
    assert resp.status_code == 200
    return resp.json()["data_quality_flag"]


def _notifications(client: TestClient) -> list[dict]:
    resp = client.get("/api/v1/sync")
    assert resp.status_code == 200
    return [n for n in resp.json()["notification"] if n["category"] == "data_quality"]


def _self_id(client: TestClient) -> str:
    resp = client.get("/api/v1/sync")
    return resp.json()["user_profile"]["id"]


class TestHardBounds:
    def test_out_of_bounds_writes_flag(self, authenticated_client: TestClient):
        _push(authenticated_client, [_measurement("steps", 999_999.0, "2026-08-14T08:00:00")])
        flags = _flags(authenticated_client)
        hard = [f for f in flags if f["kind"] == "hard_bound"]
        assert len(hard) == 1
        assert hard[0]["metric_code"] == "steps"

    def test_in_bounds_no_flag(self, authenticated_client: TestClient):
        _push(authenticated_client, [_measurement("steps", 8_000.0, "2026-08-14T08:00:00")])
        flags = _flags(authenticated_client)
        assert not [f for f in flags if f["kind"] == "hard_bound"]

    def test_flag_not_duplicated_on_update(self, authenticated_client: TestClient):
        mid = str(uuid.uuid4())
        _push(authenticated_client, [_measurement("steps", 999_999.0, "2026-08-14T08:00:00", measurement_id=mid)])
        # correcting the value still out of bounds → no second flag (dedup)
        _push(authenticated_client, [{
            "type": "update", "entity": "measurement", "id": mid,
            "data": {"value_numeric": 888_888.0},
        }])
        hard = [f for f in _flags(authenticated_client) if f["kind"] == "hard_bound"]
        assert len(hard) == 1


class TestCrossSource:
    def test_divergent_sources_flag(self, authenticated_client: TestClient):
        _push(authenticated_client, [
            _measurement("steps", 10_000.0, "2026-08-14T08:00:00", source="health_connect"),
            _measurement("steps", 4_000.0, "2026-08-14T09:00:00", source="manual"),
        ])
        cross = [f for f in _flags(authenticated_client) if f["kind"] == "cross_source"]
        assert len(cross) == 1
        assert cross[0]["metric_code"] == "steps"

    def test_agreeing_sources_no_flag(self, authenticated_client: TestClient):
        _push(authenticated_client, [
            _measurement("steps", 10_000.0, "2026-08-14T08:00:00", source="health_connect"),
            _measurement("steps", 10_200.0, "2026-08-14T09:00:00", source="manual"),
        ])
        cross = [f for f in _flags(authenticated_client) if f["kind"] == "cross_source"]
        assert cross == []

    def test_non_discrete_metric_no_cross_source_flag(self, authenticated_client: TestClient):
        _push(authenticated_client, [
            _measurement("weight", 70.0, "2026-08-14T08:00:00", source="scale"),
            _measurement("weight", 120.0, "2026-08-14T09:00:00", source="manual"),
        ])
        cross = [f for f in _flags(authenticated_client) if f["kind"] == "cross_source"]
        assert cross == []


class TestAnomalyRecheck:
    def _seed_weight_history(self, client: TestClient, outlier_id: str) -> None:
        base = datetime(2026, 8, 1, 8, 0, 0)
        ops = []
        for i in range(14):
            value = 70.0 + (i % 3) * 0.5
            ops.append(_measurement(
                "weight", value, (base + timedelta(days=i)).isoformat(),
            ))
        ops.append(_measurement("weight", 150.0, (base + timedelta(days=14)).isoformat(), measurement_id=outlier_id))
        _push(client, ops)

    def test_recheck_flags_anomaly_and_notifies(self, authenticated_client: TestClient):
        outlier_id = str(uuid.uuid4())
        self._seed_weight_history(authenticated_client, outlier_id)

        result = _push_cmd(authenticated_client, "data_quality_recheck", {})
        assert result["status"] == "ok"
        assert result["extra"]["anomaly_flags"] >= 1

        flags = _flags(authenticated_client)
        anomaly = [f for f in flags if f["kind"] == "anomaly"]
        assert any(f["measurement_id"] == outlier_id for f in anomaly)

        resp = authenticated_client.get("/api/v1/sync")
        notifications = resp.json()["notification"]
        assert any(n["category"] == "data_quality" for n in notifications)

    def test_recheck_is_idempotent(self, authenticated_client: TestClient):
        self._seed_weight_history(authenticated_client, str(uuid.uuid4()))
        _push_cmd(authenticated_client, "data_quality_recheck", {})
        second = _push_cmd(authenticated_client, "data_quality_recheck", {})
        assert second["status"] == "ok"
        assert second["extra"]["anomaly_flags"] == 0


class TestNotificationBehavior:
    def test_non_manual_out_of_bounds_notifies(self, authenticated_client: TestClient):
        _push(authenticated_client, [_measurement("steps", 999_999.0, "2026-08-14T08:00:00", source="health_connect")])
        notifications = _notifications(authenticated_client)
        assert len(notifications) == 1
        assert notifications[0]["link"] == "/entries/steps"
        assert notifications[0]["severity"] == "warning"

    def test_manual_out_of_bounds_does_not_notify(self, authenticated_client: TestClient):
        _push(authenticated_client, [_measurement("steps", 999_999.0, "2026-08-14T08:00:00", source="manual")])
        assert [f for f in _flags(authenticated_client) if f["kind"] == "hard_bound"]
        assert _notifications(authenticated_client) == []

    def test_coalescing_single_notification_per_metric_per_day(self, authenticated_client: TestClient):
        _push(authenticated_client, [
            _measurement("steps", 999_999.0, "2026-08-14T08:00:00", source="health_connect"),
            _measurement("steps", 888_888.0, "2026-08-14T09:00:00", source="health_connect"),
        ])
        assert len(_notifications(authenticated_client)) == 1


class TestToggle:
    def test_toggle_off_suppresses_notification_but_keeps_flag(self, authenticated_client: TestClient):
        user_id = _self_id(authenticated_client)
        _push(authenticated_client, [{
            "type": "update", "entity": "user", "id": user_id,
            "data": {"dq_notify_hard_bound": False},
        }])
        _push(authenticated_client, [_measurement("steps", 999_999.0, "2026-08-14T08:00:00", source="health_connect")])
        assert [f for f in _flags(authenticated_client) if f["kind"] == "hard_bound"]
        assert _notifications(authenticated_client) == []


class TestStaleFlagCleanup:
    def test_update_to_in_bounds_clears_flag(self, authenticated_client: TestClient):
        mid = str(uuid.uuid4())
        _push(authenticated_client, [_measurement("steps", 999_999.0, "2026-08-14T08:00:00", measurement_id=mid)])
        assert [f for f in _flags(authenticated_client) if f["kind"] == "hard_bound"]

        _push(authenticated_client, [{
            "type": "update", "entity": "measurement", "id": mid,
            "data": {"value_numeric": 8_000.0},
        }])
        assert [f for f in _flags(authenticated_client) if f["kind"] == "hard_bound"] == []


class TestAcknowledge:
    def test_acknowledge_sets_resolved_at(self, authenticated_client: TestClient):
        _push(authenticated_client, [_measurement("steps", 999_999.0, "2026-08-14T08:00:00")])
        flag_id = [f for f in _flags(authenticated_client) if f["kind"] == "hard_bound"][0]["id"]

        result = _push_cmd(authenticated_client, "data_quality_acknowledge", {"flag_id": flag_id})
        assert result["status"] == "updated"

        resolved = [f for f in _flags(authenticated_client) if f["id"] == flag_id][0]
        assert resolved["resolved_at"] is not None


class TestWebhookIngestion:
    def test_webhook_ingestion_creates_hard_bound_flag(self, db_engine):
        from sqlmodel import Session, select

        from salus.models import DataType
        from salus.models.data_quality import DataQualityFlag
        from salus.models.metric_definition import MetricDefinition
        from salus.models.user import User
        from salus.repositories.measurement import MeasurementRepository
        from salus.repositories.metric_definition import MetricDefinitionRepository
        from salus.services.metric_type_mapping import MetricDefinitionMappingService
        from salus.services.parser import FlexiblePayloadParser
        from salus.services.webhook_ingestion import WebhookIngestionService

        with Session(db_engine) as session:
            user = User(username="webhook_user", password_hash="x")
            session.add(user)
            session.add(MetricDefinition(
                code="steps", name="Steps", unit="steps", data_type=DataType.NUMBER,
                source_data_type="steps", sort_order=10, min_value=0.0, max_value=150_000.0,
            ))
            session.commit()
            user_id = user.id

        service = WebhookIngestionService(
            FlexiblePayloadParser(),
            MeasurementRepository(Session(db_engine)),
            MetricDefinitionMappingService(MetricDefinitionRepository(Session(db_engine))),
        )
        service.ingest(
            {"steps": [{"count": 999_999, "start_time": "2026-08-14T08:00:00"}]}, user_id
        )

        with Session(db_engine) as session:
            flags = session.exec(select(DataQualityFlag)).all()
        assert any(f.kind == "hard_bound" and f.metric_code == "steps" for f in flags)

    def test_reingestion_keeps_single_flag_with_correct_id(self, db_engine):
        from sqlmodel import Session, select

        from salus.models import DataType
        from salus.models.data_quality import DataQualityFlag
        from salus.models.measurement import Measurement
        from salus.models.metric_definition import MetricDefinition
        from salus.models.user import User
        from salus.repositories.measurement import MeasurementRepository
        from salus.repositories.metric_definition import MetricDefinitionRepository
        from salus.services.metric_type_mapping import MetricDefinitionMappingService
        from salus.services.parser import FlexiblePayloadParser
        from salus.services.webhook_ingestion import WebhookIngestionService

        with Session(db_engine) as session:
            user = User(username="webhook_user", password_hash="x")
            session.add(user)
            session.add(MetricDefinition(
                code="steps", name="Steps", unit="steps", data_type=DataType.NUMBER,
                source_data_type="steps", sort_order=10, min_value=0.0, max_value=150_000.0,
            ))
            session.commit()
            user_id = user.id

        service = WebhookIngestionService(
            FlexiblePayloadParser(),
            MeasurementRepository(Session(db_engine)),
            MetricDefinitionMappingService(MetricDefinitionRepository(Session(db_engine))),
        )
        payload = {"steps": [{"count": 999_999, "start_time": "2026-08-14T08:00:00"}]}
        service.ingest(payload, user_id)
        service.ingest(payload, user_id)  # same external_id → upsert, not insert

        with Session(db_engine) as session:
            measurements = session.exec(
                select(Measurement).where(Measurement.metric_code == "steps")
            ).all()
            flags = session.exec(select(DataQualityFlag)).all()

        hard = [f for f in flags if f.kind == "hard_bound"]
        assert len(measurements) == 1  # upsert deduplicated the row
        assert len(hard) == 1  # flag not re-created
        assert hard[0].measurement_id == measurements[0].id


class TestCleanupJob:
    def test_cleanup_job_purges_old_flags(self, db_engine):
        from datetime import timedelta, timezone

        from sqlmodel import Session, select

        from salus.models.data_quality import DataQualityFlag
        from salus.models.user import User
        from salus.services.data_quality import DataQualityCleanupJob

        with Session(db_engine) as session:
            user = User(username="cleanup_user", password_hash="x")
            session.add(user)
            session.commit()
            user_id = user.id
            session.add(DataQualityFlag(
                user_id=user_id, kind="anomaly", message="old",
                created_at=datetime.now(timezone.utc) - timedelta(days=400),
            ))
            session.add(DataQualityFlag(user_id=user_id, kind="anomaly", message="recent"))
            session.commit()

        DataQualityCleanupJob().run(lambda: Session(db_engine))

        with Session(db_engine) as session:
            flags = session.exec(select(DataQualityFlag)).all()
        assert len(flags) == 1
        assert flags[0].message == "recent"


class TestDeltaSync:
    def test_delta_includes_updated_append_only_flags(self, db_engine):
        from datetime import datetime as _dt

        from sqlmodel import Session

        from salus.models.data_quality import DataQualityFlag
        from salus.models.user import User
        from salus.repositories.unit_of_work import SqlUnitOfWork
        from salus.services.sync import SyncService

        with Session(db_engine) as session:
            user = User(username="delta_user", password_hash="x")
            session.add(user)
            session.commit()
            user_id = user.id
            flag = DataQualityFlag(
                user_id=user_id, kind="anomaly", message="resolved later",
                created_at=_dt(2026, 7, 1, 12, 0, 0),
                updated_at=_dt(2026, 8, 1, 12, 0, 0),
            )
            session.add(flag)
            session.commit()
            flag_id = flag.id

        with Session(db_engine) as session:
            user = session.get(User, user_id)
            result = SyncService(SqlUnitOfWork(session)).delta_sync(
                user, _dt(2026, 7, 15, 0, 0, 0)
            )
            changed_flags = result["changed"].get("data_quality_flag", [])
        assert any(f.id == flag_id for f in changed_flags)
