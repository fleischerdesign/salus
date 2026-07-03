import pytest
import json
from datetime import datetime, timezone, date
from pathlib import Path
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from salus.models.user import User as UserModel
from salus.models import MetricType, DataType
from salus.models.measurement import Measurement
from salus.models.sharing import ConnectionStatus, SharingRelationship
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services.sharing import SharingService
from salus.services.leaderboard import LeaderboardService
from salus.exceptions import NotFoundError, ConflictError
from salus.services._helpers import uid


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


@pytest.fixture
def seeded_users(session: Session):
    uow = SqlUnitOfWork(session)
    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        grantee = UserModel(username="grantee", password_hash="hash")
        uow.users.add(owner)
        uow.users.add(grantee)
        uow.commit()
        owner_id = uid(owner)
        grantee_id = uid(grantee)

        metric = MetricType(
            name="Steps",
            unit="steps",
            data_type=DataType.NUMBER,
            user_id=owner_id,
            is_system=True,
            widget_enabled=True,
            source_data_type="steps",
        )
        uow.metric_types.add(metric)
        uow.commit()
        assert metric.id is not None
        metric_id = metric.id

    return {
        "uow": uow,
        "owner_id": owner_id,
        "grantee_id": grantee_id,
        "metric_id": metric_id,
    }


# ---------------------------------------------------------------------------
# SharingRelationship creation & status
# ---------------------------------------------------------------------------

def test_create_relationship_creates_pending(session: Session):
    uow = SqlUnitOfWork(session)
    service = SharingService(uow)

    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        grantee = UserModel(username="grantee", password_hash="hash")
        uow.users.add(owner)
        uow.users.add(grantee)
        uow.commit()
        owner_id = uid(owner)

        metric = MetricType(
            name="Steps", unit="steps", data_type=DataType.NUMBER,
            user_id=owner_id, is_system=True, source_data_type="steps",
        )
        uow.metric_types.add(metric)
        uow.commit()
        assert metric.id is not None
        metric_id = metric.id

    rel = service.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    assert rel.id is not None
    assert rel.status == ConnectionStatus.PENDING
    assert rel.is_active is False


def test_create_relationship_rejects_duplicate_pending(session: Session):
    uow = SqlUnitOfWork(session)
    service = SharingService(uow)

    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        grantee = UserModel(username="grantee", password_hash="hash")
        uow.users.add(owner)
        uow.users.add(grantee)
        uow.commit()
        owner_id = uid(owner)

        metric = MetricType(
            name="Steps", unit="steps", data_type=DataType.NUMBER,
            user_id=owner_id, is_system=True, source_data_type="steps",
        )
        uow.metric_types.add(metric)
        uow.commit()
        assert metric.id is not None
        metric_id = metric.id

    service.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    with pytest.raises(ConflictError):
        service.create_relationship(
            owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
        )


def test_create_relationship_remote_no_local_check(session: Session):
    uow = SqlUnitOfWork(session)
    service = SharingService(uow)

    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        uow.users.add(owner)
        uow.commit()
        owner_id = uid(owner)

        metric = MetricType(
            name="Steps", unit="steps", data_type=DataType.NUMBER,
            user_id=owner_id, is_system=True, source_data_type="steps",
        )
        uow.metric_types.add(metric)
        uow.commit()
        assert metric.id is not None
        metric_id = metric.id

    rel = service.create_relationship(
        owner_id=owner_id, grantee_handle="@alice:remote-server.com",
        metric_type_id=metric_id,
    )
    assert rel.id is not None
    assert rel.grantee_handle == "@alice:remote-server.com"
    assert rel.status == ConnectionStatus.PENDING
    assert rel.api_token_hash is not None


# ---------------------------------------------------------------------------
# Accept / Decline
# ---------------------------------------------------------------------------

def test_accept_relationship(seeded_users):
    svc = SharingService(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    assert rel.status == ConnectionStatus.PENDING

    accepted = svc.accept_relationship(grantee_id, rel.id)
    assert accepted.status == ConnectionStatus.ACTIVE
    assert accepted.is_active is True


def test_decline_relationship(seeded_users):
    svc = SharingService(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    assert rel.status == ConnectionStatus.PENDING

    declined = svc.decline_relationship(grantee_id, rel.id)
    assert declined.status == ConnectionStatus.DECLINED


def test_accept_wrong_grantee_raises(seeded_users):
    svc = SharingService(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    metric_id = seeded_users["metric_id"]

    with uow:
        third_user = UserModel(username="third", password_hash="hash")
        uow.users.add(third_user)
        uow.commit()

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee",
        metric_type_id=metric_id,
    )

    with pytest.raises(NotFoundError):
        svc.accept_relationship(uid(third_user), rel.id)


def test_accept_twice_raises(seeded_users):
    svc = SharingService(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    svc.accept_relationship(grantee_id, rel.id)

    with pytest.raises(ConflictError):
        svc.accept_relationship(grantee_id, rel.id)


# ---------------------------------------------------------------------------
# Deactivate (revoke)
# ---------------------------------------------------------------------------

def test_deactivate_relationship(seeded_users):
    svc = SharingService(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    svc.accept_relationship(grantee_id, rel.id)

    svc.deactivate_relationship(owner_id, rel.id)
    with seeded_users["uow"]:
        updated = seeded_users["uow"].sharing_relationships.get_by_id(rel.id)
        assert updated is not None
        assert updated.status == ConnectionStatus.REVOKED


# ---------------------------------------------------------------------------
# Resolution — data access after acceptance
# ---------------------------------------------------------------------------

def test_resolution_requires_acceptance(seeded_users):
    svc = SharingService(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    t_utc = datetime(2026, 7, 2, 10, 0, tzinfo=timezone.utc)
    with uow:
        m = Measurement(
            user_id=owner_id, metric_type_id=metric_id, data_type="steps",
            value_numeric=5000.0, start_time=t_utc, source="manual", external_id="m1",
        )
        uow.measurements.add(m)
        uow.commit()

    svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
        aggregation_level="daily_summary",
    )

    with pytest.raises(PermissionError):
        svc.resolve_and_fetch(
            requester_id=grantee_id, owner_handle="@owner",
            data_type="steps", date_str="2026-07-02",
        )

    # Accept then retry
    with uow:
        rels = uow.sharing_relationships.find_by_owner(owner_id)
        rel = rels[0]
        svc.accept_relationship(grantee_id, rel.id)

    data = svc.resolve_and_fetch(
        requester_id=grantee_id, owner_handle="@owner",
        data_type="steps", date_str="2026-07-02",
    )
    assert len(data) == 1
    assert data[0]["value_numeric"] == 5000.0


def test_resolution_after_revoke_denies(seeded_users):
    svc = SharingService(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    t_utc = datetime(2026, 7, 2, 10, 0, tzinfo=timezone.utc)
    with uow:
        m = Measurement(
            user_id=owner_id, metric_type_id=metric_id, data_type="steps",
            value_numeric=8000.0, start_time=t_utc, source="manual", external_id="m1",
        )
        uow.measurements.add(m)
        uow.commit()

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    svc.accept_relationship(grantee_id, rel.id)
    svc.deactivate_relationship(owner_id, rel.id)

    with pytest.raises(PermissionError):
        svc.resolve_and_fetch(
            requester_id=grantee_id, owner_handle="@owner",
            data_type="steps", date_str="2026-07-02",
        )


# ---------------------------------------------------------------------------
# Peer connections (merged view)
# ---------------------------------------------------------------------------

def test_get_peer_connections_outgoing(seeded_users):
    svc = SharingService(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    svc.accept_relationship(grantee_id, rel.id)

    peers = svc.get_peer_connections(owner_id)
    assert len(peers) == 1
    assert peers[0].handle == "@grantee"
    assert peers[0].is_mutual is False
    assert any(m.metric_name == "Steps" and m.direction == "outgoing" for m in peers[0].metrics)


def test_get_peer_connections_mutual(seeded_users):
    svc = SharingService(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    with uow:
        grantee_metric = MetricType(
            name="Heart Rate", unit="bpm", data_type=DataType.NUMBER,
            user_id=grantee_id, is_system=True, source_data_type="heart_rate",
        )
        uow.metric_types.add(grantee_metric)
        uow.commit()
        assert grantee_metric.id is not None
        grantee_metric_id = grantee_metric.id

    # Owner -> Grantee
    rel1 = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    svc.accept_relationship(grantee_id, rel1.id)

    # Grantee -> Owner
    rel2 = svc.create_relationship(
        owner_id=grantee_id, grantee_handle="@owner",
        metric_type_id=grantee_metric_id,
    )
    with uow:
        owner_user = uow.users.get_by_id(owner_id)
        assert owner_user is not None
    svc.accept_relationship(owner_id, rel2.id)

    # From owner's view: one peer, mutual
    peers = svc.get_peer_connections(owner_id)
    assert len(peers) == 1
    assert peers[0].handle == "@grantee"
    assert peers[0].is_mutual is True
    assert len(peers[0].metrics) == 2


def test_get_peer_connections_incoming(seeded_users):
    svc = SharingService(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    svc.accept_relationship(grantee_id, rel.id)

    # From grantee's view: one incoming peer
    peers = svc.get_peer_connections(grantee_id)
    assert len(peers) == 1
    assert peers[0].handle == "@owner"
    assert peers[0].is_mutual is False
    assert any(m.direction == "incoming" for m in peers[0].metrics)


def test_get_pending_invitations(seeded_users):
    svc = SharingService(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )

    pending = svc.get_pending_invitations(grantee_id)
    assert len(pending) == 1
    assert pending[0].status == ConnectionStatus.PENDING


def test_get_pending_invitations_empty_after_accept(seeded_users):
    svc = SharingService(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    svc.accept_relationship(grantee_id, rel.id)

    pending = svc.get_pending_invitations(grantee_id)
    assert len(pending) == 0


# ---------------------------------------------------------------------------
# Federation API endpoint
# ---------------------------------------------------------------------------

def test_federated_api_endpoint(session: Session):
    from salus.main import app
    from salus.dependencies import get_session

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    app.dependency_overrides[get_session] = lambda: Session(engine)

    uow = SqlUnitOfWork(Session(engine))
    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        uow.users.add(owner)
        uow.commit()
        owner_id = uid(owner)

        metric = MetricType(
            name="Steps", unit="steps", data_type=DataType.NUMBER,
            user_id=owner_id, is_system=True, source_data_type="steps",
        )
        uow.metric_types.add(metric)
        uow.commit()
        assert metric.id is not None
        metric_id = metric.id

        m = Measurement(
            user_id=owner_id, metric_type_id=metric_id, data_type="steps",
            value_numeric=9500.0,
            start_time=datetime(2026, 7, 2, 10, 0, tzinfo=timezone.utc),
            source="manual", external_id="m-api",
        )
        uow.measurements.add(m)
        uow.commit()

    svc = SharingService(uow)
    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@alice:external-server.com",
        metric_type_id=metric_id, aggregation_level="raw",
    )
    token = rel.api_token_hash

    with TestClient(app) as client:
        # Pending relationship — should NOT have access yet
        response = client.get(
            "/api/v1/federation/sharing",
            params={"owner_username": "owner", "data_type": "steps", "date": "2026-07-02"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401

    # Accept via direct status update (simulating federation accept callback)
    with uow:
        db_rel = uow.sharing_relationships.get_by_id(rel.id)
        assert db_rel is not None
        db_rel.status = ConnectionStatus.ACTIVE
        uow.sharing_relationships.update(db_rel)
        uow.commit()

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/federation/sharing",
            params={"owner_username": "owner", "data_type": "steps", "date": "2026-07-02"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        res_data = response.json()
        assert res_data["status"] == "ok"
        assert len(res_data["data"]) == 1
        assert res_data["data"][0]["value_numeric"] == 9500.0

        # Invalid token
        response = client.get(
            "/api/v1/federation/sharing",
            params={"owner_username": "owner", "data_type": "steps", "date": "2026-07-02"},
            headers={"Authorization": "Bearer invalid"},
        )
        assert response.status_code == 401

    app.dependency_overrides.clear()


def test_federation_accept_endpoint(session: Session):
    from salus.main import app
    from salus.dependencies import get_session, get_sharing_service

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    uow = SqlUnitOfWork(Session(engine))
    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        uow.users.add(owner)
        uow.commit()
        owner_id = uid(owner)

        metric = MetricType(
            name="Steps", unit="steps", data_type=DataType.NUMBER,
            user_id=owner_id, is_system=True, source_data_type="steps",
        )
        uow.metric_types.add(metric)
        uow.commit()
        assert metric.id is not None
        metric_id = metric.id

    svc = SharingService(uow)
    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@alice:external-server.com",
        metric_type_id=metric_id,
    )
    assert rel.status == ConnectionStatus.PENDING
    token = rel.api_token_hash

    app.dependency_overrides[get_session] = lambda: Session(engine)
    app.dependency_overrides[get_sharing_service] = lambda: SharingService(uow)

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/federation/accept",
            json={"token": token, "owner_handle": "@owner"},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    with uow:
        updated = uow.sharing_relationships.get_by_id(rel.id)
        assert updated is not None
        assert updated.status == ConnectionStatus.ACTIVE

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Sharing POST route
# ---------------------------------------------------------------------------

def test_sharing_post_route():
    from salus.main import app
    from salus.dependencies import get_session, get_current_user

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    uow = SqlUnitOfWork(Session(engine))
    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        uow.users.add(owner)
        uow.commit()
        owner_id = uid(owner)

        m1 = MetricType(
            name="Steps", unit="steps", data_type=DataType.NUMBER,
            user_id=owner_id, is_system=True, source_data_type="steps",
        )
        m2 = MetricType(
            name="Weight", unit="kg", data_type=DataType.NUMBER,
            user_id=owner_id, is_system=True, source_data_type="weight",
        )
        uow.metric_types.add(m1)
        uow.metric_types.add(m2)
        uow.commit()
        assert m1.id is not None
        assert m2.id is not None
        m1_id = m1.id
        m2_id = m2.id

    app.dependency_overrides[get_session] = lambda: Session(engine)
    app.dependency_overrides[get_current_user] = lambda: owner

    with TestClient(app) as client:
        response = client.post(
            "/sharing",
            data={
                "grantee_handle": "@grantee:external.com",
                "metric_type_ids": [str(m1_id), str(m2_id)],
                f"aggregation_level_{m1_id}": "raw",
                f"aggregation_level_{m2_id}": "daily_summary",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303

        with uow:
            rels = uow.sharing_relationships.find_by_owner(owner_id)
            assert len(rels) == 2
            # Both are pending
            assert all(r.status == ConnectionStatus.PENDING for r in rels)
            assert {r.metric_type_id for r in rels} == {m1_id, m2_id}
            m1_rel = next(r for r in rels if r.metric_type_id == m1_id)
            m2_rel = next(r for r in rels if r.metric_type_id == m2_id)
            assert m1_rel.aggregation_level == "raw"
            assert m2_rel.aggregation_level == "daily_summary"

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Expiration
# ---------------------------------------------------------------------------

def test_sharing_expiration_after_acceptance(seeded_users):
    svc = SharingService(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    t_utc = datetime.now(timezone.utc)
    with uow:
        m = Measurement(
            user_id=owner_id, metric_type_id=metric_id, data_type="steps",
            value_numeric=12000.0, start_time=t_utc, source="manual", external_id="m-exp",
        )
        uow.measurements.add(m)
        uow.commit()

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
        expiration_days=-1,
    )
    svc.accept_relationship(grantee_id, rel.id)

    # Access should be denied due to expiration (even though status is active,
    # get_active_relationship checks expiration date)
    with pytest.raises(PermissionError):
        svc.resolve_and_fetch(
            requester_id=grantee_id, owner_handle="@owner",
            data_type="steps",
            date_str=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        )

    # Remove expiration
    with uow:
        db_rel = uow.sharing_relationships.get_by_id(rel.id)
        assert db_rel is not None
        db_rel.expiration_date = None
        uow.sharing_relationships.update(db_rel)
        uow.commit()

    res = svc.resolve_and_fetch(
        requester_id=grantee_id, owner_handle="@owner",
        data_type="steps",
        date_str=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )
    assert len(res) == 1
    assert res[0]["value_numeric"] == 12000.0


def test_resolution_invalid_date_fallback(seeded_users):
    svc = SharingService(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    t_utc = datetime.now(timezone.utc)
    with uow:
        m = Measurement(
            user_id=owner_id, metric_type_id=metric_id, data_type="steps",
            value_numeric=12000.0, start_time=t_utc, source="manual", external_id="m-fallback",
        )
        uow.measurements.add(m)
        uow.commit()

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_type_id=metric_id,
    )
    svc.accept_relationship(grantee_id, rel.id)

    res = svc.resolve_and_fetch(
        requester_id=grantee_id, owner_handle="@owner",
        data_type="steps", date_str="invalid-date-string",
    )
    assert len(res) == 1
    assert res[0]["value_numeric"] == 12000.0


# ---------------------------------------------------------------------------
# Leaderboard with acceptance requirement
# ---------------------------------------------------------------------------

def test_leaderboard_connection_prerequisite(seeded_users):
    uow = seeded_users["uow"]
    svc = SharingService(uow)
    leaderboard_svc = LeaderboardService(uow)
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    with uow:
        grantee_metric = MetricType(
            name="Steps", unit="steps", data_type=DataType.NUMBER,
            user_id=grantee_id, is_system=True, source_data_type="steps",
        )
        uow.metric_types.add(grantee_metric)
        uow.commit()
        assert grantee_metric.id is not None
        grantee_metric_id = grantee_metric.id

    group = leaderboard_svc.create_group(
        creator_id=owner_id, name="Step Challenge",
        metric_type_code="steps", time_frame="weekly",
    )
    assert group.id is not None

    # Without connection: should fail
    with pytest.raises(PermissionError) as exc_info:
        leaderboard_svc.join_by_code(grantee_id, group.invite_code)
    assert "connected" in str(exc_info.value)

    # Create and accept sharing relationship
    rel = svc.create_relationship(
        owner_id=grantee_id, grantee_handle="@owner",
        metric_type_id=grantee_metric_id,
    )
    svc.accept_relationship(owner_id, rel.id)

    # Now join should succeed
    joined = leaderboard_svc.join_by_code(grantee_id, group.invite_code)
    assert joined.id == group.id


def test_leaderboard_rankings(seeded_users):
    uow = seeded_users["uow"]
    svc = SharingService(uow)
    leaderboard_svc = LeaderboardService(uow)
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_id = seeded_users["metric_id"]

    with uow:
        grantee_metric = MetricType(
            name="Steps", unit="steps", data_type=DataType.NUMBER,
            user_id=grantee_id, is_system=True, source_data_type="steps",
        )
        uow.metric_types.add(grantee_metric)
        uow.commit()
        assert grantee_metric.id is not None
        grantee_metric_id = grantee_metric.id

    group = leaderboard_svc.create_group(
        creator_id=owner_id, name="Step Challenge",
        metric_type_code="steps", time_frame="weekly",
    )
    assert group.id is not None

    rel = svc.create_relationship(
        owner_id=grantee_id, grantee_handle="@owner",
        metric_type_id=grantee_metric_id,
    )
    svc.accept_relationship(owner_id, rel.id)
    leaderboard_svc.join_by_code(grantee_id, group.invite_code)

    t_utc = datetime.now(timezone.utc)
    with uow:
        m_creator = Measurement(
            user_id=owner_id, metric_type_id=metric_id, data_type="steps",
            value_numeric=10000.0, start_time=t_utc, source="manual", external_id="m_c",
        )
        m_invitee = Measurement(
            user_id=grantee_id, metric_type_id=grantee_metric_id, data_type="steps",
            value_numeric=15000.0, start_time=t_utc, source="manual", external_id="m_i",
        )
        uow.measurements.add(m_creator)
        uow.measurements.add(m_invitee)
        uow.commit()

    assert group.id is not None
    rankings_data = leaderboard_svc.get_group_rankings(group.id, owner_id)
    rankings = rankings_data["rankings"]
    assert rankings[0]["username"] == "grantee"
    assert rankings[0]["score"] == 15000.0
    assert rankings[1]["username"] == "owner"
    assert rankings[1]["score"] == 10000.0


# ---------------------------------------------------------------------------
# Leaderboard routes
# ---------------------------------------------------------------------------

def test_leaderboard_routes():
    from salus.main import app
    from salus.dependencies import get_session, get_current_user

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    uow = SqlUnitOfWork(Session(engine))
    with uow:
        creator = UserModel(username="creator", password_hash="hash")
        invitee = UserModel(username="invitee", password_hash="hash")
        uow.users.add(creator)
        uow.users.add(invitee)
        uow.commit()
        creator_id = uid(creator)
        invitee_id = uid(invitee)

        metric_i = MetricType(
            name="Steps", unit="steps", data_type=DataType.NUMBER,
            user_id=invitee_id, is_system=True, source_data_type="steps",
        )
        uow.metric_types.add(metric_i)
        uow.commit()
        assert metric_i.id is not None
        metric_i_id = metric_i.id

    app.dependency_overrides[get_session] = lambda: Session(engine)

    with TestClient(app) as client:
        app.dependency_overrides[get_current_user] = lambda: creator
        response = client.get("/sharing/leaderboard")
        assert response.status_code == 200

        response = client.post(
            "/sharing/leaderboard/create",
            data={
                "name": "Step Challenge 2026",
                "metric_type_code": "steps",
                "time_frame": "weekly",
            },
            follow_redirects=False,
        )
        assert response.status_code == 303
        redirect_url = response.headers["location"]
        group_id = int(redirect_url.split("/")[-1])

        with uow:
            group = uow.leaderboard_groups.get_by_id(group_id)
            assert group is not None
            invite_code = group.invite_code

        # Invitee tries to join without connection -> redirect with error
        app.dependency_overrides[get_current_user] = lambda: invitee
        response = client.post(
            "/sharing/leaderboard/join",
            data={"invite_code": invite_code},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert "error=" in response.headers["location"]

        # Create and accept connection
        svc = SharingService(uow)
        rel = svc.create_relationship(
            owner_id=invitee_id, grantee_handle="@creator",
            metric_type_id=metric_i_id,
        )
        svc.accept_relationship(creator_id, rel.id)

        # Now join succeeds
        response = client.post(
            "/sharing/leaderboard/join",
            data={"invite_code": invite_code},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == f"/sharing/leaderboard/{group_id}"

        # Leave
        response = client.post(
            f"/sharing/leaderboard/{group_id}/leave",
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/sharing/leaderboard"

        # Creator deletes
        app.dependency_overrides[get_current_user] = lambda: creator
        response = client.post(
            f"/sharing/leaderboard/{group_id}/delete",
            follow_redirects=False,
        )
        assert response.status_code == 303

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Connections page route
# ---------------------------------------------------------------------------

def test_connections_page():
    from salus.main import app
    from salus.dependencies import get_session, get_current_user

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    uow = SqlUnitOfWork(Session(engine))
    with uow:
        user = UserModel(username="testuser", password_hash="hash")
        uow.users.add(user)
        uow.commit()

    app.dependency_overrides[get_session] = lambda: Session(engine)
    app.dependency_overrides[get_current_user] = lambda: user

    with TestClient(app) as client:
        response = client.get("/sharing/connections")
        assert response.status_code == 200
        assert "Connections" in response.text
        assert "Invite a Peer" in response.text

    app.dependency_overrides.clear()


def test_invite_modal_route():
    from salus.main import app
    from salus.dependencies import get_session, get_current_user

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    uow = SqlUnitOfWork(Session(engine))
    with uow:
        user = UserModel(username="testuser", password_hash="hash")
        uow.users.add(user)
        uow.commit()

    app.dependency_overrides[get_session] = lambda: Session(engine)
    app.dependency_overrides[get_current_user] = lambda: user

    with TestClient(app) as client:
        response = client.get("/sharing/connections/invite-modal")
        assert response.status_code == 200
        assert "qrserver.com" in response.text

    app.dependency_overrides.clear()
