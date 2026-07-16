import pytest
from datetime import datetime, timezone
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from salus.models.user import User as UserModel
from salus.models.metric_definition import MetricDefinition
from salus.models.measurement import Measurement
from salus.models.sharing import ConnectionStatus
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services.sharing import SharingService
from salus.services.leaderboard import LeaderboardService
from salus.exceptions import ForbiddenError, NotFoundError, ConflictError
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

        metric_def = MetricDefinition(code="sharing_test_steps", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric_def)
        uow.commit()
        metric_code = metric_def.code

    return {
        "uow": uow,
        "owner_id": owner_id,
        "grantee_id": grantee_id,
        "metric_code": metric_code,
    }


# ---------------------------------------------------------------------------
# SharingRelationship creation & status
# ---------------------------------------------------------------------------

def test_create_relationship_creates_pending(session: Session):
    uow = SqlUnitOfWork(session)
    service = SharingService.create(uow)

    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        grantee = UserModel(username="grantee", password_hash="hash")
        uow.users.add(owner)
        uow.users.add(grantee)
        uow.commit()
        owner_id = uid(owner)

        metric_def = MetricDefinition(code="sharing_test_steps_1", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric_def)
        uow.commit()
        metric_code = metric_def.code

    rel = service.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
    )
    assert rel.id is not None
    assert rel.status == ConnectionStatus.PENDING
    assert rel.is_active is False


def test_create_relationship_rejects_duplicate_pending(session: Session):
    uow = SqlUnitOfWork(session)
    service = SharingService.create(uow)

    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        grantee = UserModel(username="grantee", password_hash="hash")
        uow.users.add(owner)
        uow.users.add(grantee)
        uow.commit()
        owner_id = uid(owner)

        metric_def = MetricDefinition(code="sharing_test_steps_2", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric_def)
        uow.commit()
        metric_code = metric_def.code

    service.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
    )
    with pytest.raises(ConflictError):
        service.create_relationship(
            owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
        )


def test_create_relationship_remote_no_local_check(session: Session):
    uow = SqlUnitOfWork(session)
    service = SharingService.create(uow)

    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        uow.users.add(owner)
        uow.commit()
        owner_id = uid(owner)

        metric_def = MetricDefinition(code="sharing_test_steps_3", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric_def)
        uow.commit()
        metric_code = metric_def.code

    rel = service.create_relationship(
        owner_id=owner_id, grantee_handle="@alice:remote-server.com",
        metric_code=metric_code,
    )
    assert rel.id is not None
    assert rel.grantee_handle == "@alice:remote-server.com"
    assert rel.status == ConnectionStatus.PENDING
    assert rel.api_token_hash is not None


# ---------------------------------------------------------------------------
# Accept / Decline
# ---------------------------------------------------------------------------

def test_accept_relationship(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
    )
    assert rel.status == ConnectionStatus.PENDING

    accepted = svc.accept_relationship(grantee_id, rel.id)
    assert accepted.status == ConnectionStatus.ACTIVE
    assert accepted.is_active is True


def test_decline_relationship(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
    )
    assert rel.status == ConnectionStatus.PENDING

    declined = svc.decline_relationship(grantee_id, rel.id)
    assert declined.status == ConnectionStatus.DECLINED


def test_accept_wrong_grantee_raises(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    metric_code = seeded_users["metric_code"]

    with uow:
        third_user = UserModel(username="third", password_hash="hash")
        uow.users.add(third_user)
        uow.commit()

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee",
        metric_code=metric_code,
    )

    with pytest.raises(NotFoundError):
        svc.accept_relationship(uid(third_user), rel.id)


def test_accept_twice_raises(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
    )
    svc.accept_relationship(grantee_id, rel.id)

    with pytest.raises(ConflictError):
        svc.accept_relationship(grantee_id, rel.id)


# ---------------------------------------------------------------------------
# Deactivate (revoke)
# ---------------------------------------------------------------------------

def test_deactivate_relationship(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
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
    svc = SharingService.create(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    t_utc = datetime(2026, 7, 2, 10, 0, tzinfo=timezone.utc)
    with uow:
        m = Measurement(
            user_id=owner_id, metric_code=metric_code, data_type="steps",
            value_numeric=5000.0, start_time=t_utc, source="manual", external_id="m1",
        )
        uow.measurements.add(m)
        uow.commit()

    svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
        aggregation_level="daily_summary",
    )

    with pytest.raises(ForbiddenError):
        svc.resolve_and_fetch(
            requester_id=grantee_id, owner_handle="@owner",
            data_type="steps", date_str="2026-07-02",
        )

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
    svc = SharingService.create(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    t_utc = datetime(2026, 7, 2, 10, 0, tzinfo=timezone.utc)
    with uow:
        m = Measurement(
            user_id=owner_id, metric_code=metric_code, data_type="steps",
            value_numeric=8000.0, start_time=t_utc, source="manual", external_id="m1",
        )
        uow.measurements.add(m)
        uow.commit()

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
    )
    svc.accept_relationship(grantee_id, rel.id)
    svc.deactivate_relationship(owner_id, rel.id)

    with pytest.raises(ForbiddenError):
        svc.resolve_and_fetch(
            requester_id=grantee_id, owner_handle="@owner",
            data_type="steps", date_str="2026-07-02",
        )


# ---------------------------------------------------------------------------
# Peer connections (merged view)
# ---------------------------------------------------------------------------

def test_get_peer_connections_outgoing(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
    )
    svc.accept_relationship(grantee_id, rel.id)

    peers = svc.get_peer_connections(owner_id)
    assert len(peers) == 1
    assert peers[0].handle == "@grantee"
    assert peers[0].is_mutual is False
    assert any(m.metric_name == "Steps" and m.direction == "outgoing" for m in peers[0].metrics)


def test_get_peer_connections_mutual(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    with uow:
        grantee_metric = MetricDefinition(code="sharing_test_hr", name="Heart Rate", unit="bpm", source_data_type="heart_rate")
        uow.metric_definitions.add(grantee_metric)
        uow.commit()
        grantee_metric_code = grantee_metric.code

    rel1 = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
    )
    svc.accept_relationship(grantee_id, rel1.id)

    rel2 = svc.create_relationship(
        owner_id=grantee_id, grantee_handle="@owner",
        metric_code=grantee_metric_code,
    )
    with uow:
        owner_user = uow.users.get_by_id(owner_id)
        assert owner_user is not None
    svc.accept_relationship(owner_id, rel2.id)

    peers = svc.get_peer_connections(owner_id)
    assert len(peers) == 1
    assert peers[0].handle == "@grantee"
    assert peers[0].is_mutual is True
    assert len(peers[0].metrics) == 2


def test_get_peer_connections_incoming(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
    )
    svc.accept_relationship(grantee_id, rel.id)

    peers = svc.get_peer_connections(grantee_id)
    assert len(peers) == 1
    assert peers[0].handle == "@owner"
    assert peers[0].is_mutual is False
    assert any(m.direction == "incoming" for m in peers[0].metrics)


def test_get_pending_invitations(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
    )

    pending = svc.get_pending_invitations(grantee_id)
    assert len(pending) == 1
    assert pending[0].status == ConnectionStatus.PENDING


def test_get_pending_invitations_empty_after_accept(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
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

        metric_def = MetricDefinition(code="fed_api_steps", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric_def)
        uow.commit()
        metric_code = metric_def.code

        m = Measurement(
            user_id=owner_id, metric_code=metric_code, data_type="steps",
            value_numeric=9500.0,
            start_time=datetime(2026, 7, 2, 10, 0, tzinfo=timezone.utc),
            source="manual", external_id="m-api",
        )
        uow.measurements.add(m)
        uow.commit()

    svc = SharingService.create(uow)
    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@alice:external-server.com",
        metric_code=metric_code, aggregation_level="raw",
    )
    token = rel.raw_token

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/federation/sharing",
            params={"owner_username": "owner", "data_type": "steps", "date": "2026-07-02"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401

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

        metric_def = MetricDefinition(code="fed_accept_steps", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric_def)
        uow.commit()
        metric_code = metric_def.code

    svc = SharingService.create(uow)
    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@alice:external-server.com",
        metric_code=metric_code,
    )
    assert rel.status == ConnectionStatus.PENDING
    token = rel.raw_token

    app.dependency_overrides[get_session] = lambda: Session(engine)
    app.dependency_overrides[get_sharing_service] = lambda: SharingService.create(uow)

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
# Sharing API routes (JSON)
# ---------------------------------------------------------------------------

def test_sharing_connections_api():
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

        m1 = MetricDefinition(code="sharing_api_test_steps", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(m1)
        uow.commit()
        m1_code = m1.code

    app.dependency_overrides[get_session] = lambda: Session(engine)
    app.dependency_overrides[get_current_user] = lambda: owner

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/sharing/connections",
            json={
                "grantee_handle": "@grantee:external.com",
                "metric_code": m1_code,
                "aggregation_level": "raw",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["grantee_handle"] == "@grantee:external.com"

        response = client.get("/api/v1/sharing/connections")
        assert response.status_code == 200
        connections = response.json()
        assert len(connections) == 1
        assert connections[0]["handle"] == "@grantee:external.com"

    app.dependency_overrides.clear()


def test_sharing_feed_api():
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
        response = client.get("/api/v1/sharing/feed")
        assert response.status_code == 200

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Expiration
# ---------------------------------------------------------------------------

def test_sharing_expiration_after_acceptance(seeded_users):
    svc = SharingService.create(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    t_utc = datetime.now(timezone.utc)
    with uow:
        m = Measurement(
            user_id=owner_id, metric_code=metric_code, data_type="steps",
            value_numeric=12000.0, start_time=t_utc, source="manual", external_id="m-exp",
        )
        uow.measurements.add(m)
        uow.commit()

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
        expiration_days=-1,
    )
    svc.accept_relationship(grantee_id, rel.id)

    with pytest.raises(ForbiddenError):
        svc.resolve_and_fetch(
            requester_id=grantee_id, owner_handle="@owner",
            data_type="steps",
            date_str=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        )

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
    svc = SharingService.create(seeded_users["uow"])
    uow = seeded_users["uow"]
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]
    metric_code = seeded_users["metric_code"]

    t_utc = datetime.now(timezone.utc)
    with uow:
        m = Measurement(
            user_id=owner_id, metric_code=metric_code, data_type="steps",
            value_numeric=12000.0, start_time=t_utc, source="manual", external_id="m-fallback",
        )
        uow.measurements.add(m)
        uow.commit()

    rel = svc.create_relationship(
        owner_id=owner_id, grantee_handle="@grantee", metric_code=metric_code,
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
    svc = SharingService.create(uow)
    leaderboard_svc = LeaderboardService(uow)
    owner_id = seeded_users["owner_id"]
    grantee_id = seeded_users["grantee_id"]

    with uow:
        grantee_metric = MetricDefinition(code="lb_steps_grantee", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(grantee_metric)
        uow.commit()
        grantee_metric_code = grantee_metric.code

    group = leaderboard_svc.create_group(
        creator_id=owner_id, name="Step Challenge",
        metric_type_code="steps", time_frame="weekly",
    )
    assert group.id is not None

    with pytest.raises(ForbiddenError) as exc_info:
        leaderboard_svc.join_by_code(grantee_id, group.invite_code)
    assert "connected" in str(exc_info.value)

    rel = svc.create_relationship(
        owner_id=grantee_id, grantee_handle="@owner",
        metric_code=grantee_metric_code,
    )
    svc.accept_relationship(owner_id, rel.id)

    joined = leaderboard_svc.join_by_code(grantee_id, group.invite_code)
    assert joined.id == group.id


    def test_leaderboard_rankings(seeded_users):
        uow = seeded_users["uow"]
        svc = SharingService.create(uow)
        leaderboard_svc = LeaderboardService(uow)
        owner_id = seeded_users["owner_id"]
        grantee_id = seeded_users["grantee_id"]
        metric_code = seeded_users["metric_code"]
    
        with uow:
            grantee_metric = MetricDefinition(code="lb_steps_grantee_2", name="Steps", unit="steps", source_data_type="steps")
            uow.metric_definitions.add(grantee_metric)
            uow.commit()
            grantee_metric_code = grantee_metric.code
    
        group = leaderboard_svc.create_group(
            creator_id=owner_id, name="Step Challenge",
            metric_type_code="steps", time_frame="weekly",
        )
        assert group.id is not None
    
        rel = svc.create_relationship(
            owner_id=grantee_id, grantee_handle="@owner",
            metric_code=grantee_metric_code,
        )
        svc.accept_relationship(owner_id, rel.id)
        leaderboard_svc.join_by_code(grantee_id, group.invite_code)
    
        t_utc = datetime.now(timezone.utc)
        with uow:
            m_creator = Measurement(
                user_id=owner_id, metric_code=metric_code, data_type="steps",
                value_numeric=10000.0, start_time=t_utc, source="manual", external_id="m_c",
            )
            m_invitee = Measurement(
                user_id=grantee_id, metric_code=grantee_metric_code, data_type="steps",
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
# Leaderboard API routes
# ---------------------------------------------------------------------------

def test_leaderboard_api_routes():
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

        metric_i = MetricDefinition(code="lb_api_steps", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric_i)
        uow.commit()
        metric_i_code = metric_i.code

    app.dependency_overrides[get_session] = lambda: Session(engine)

    with TestClient(app) as client:
        app.dependency_overrides[get_current_user] = lambda: creator

        response = client.get("/api/v1/sharing/leaderboard")
        assert response.status_code == 200
        assert response.json() == []

        response = client.post(
            "/api/v1/sharing/leaderboard",
            json={
                "name": "Step Challenge 2026",
                "metric_type_code": "steps",
                "time_frame": "weekly",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Step Challenge 2026"
        group_id = data["id"]

        app.dependency_overrides[get_current_user] = lambda: invitee
        svc = SharingService.create(uow)
        rel = svc.create_relationship(
            owner_id=invitee_id, grantee_handle="@creator",
            metric_code=metric_i_code,
        )
        svc.accept_relationship(creator_id, rel.id)

        response = client.post(
            f"/api/v1/sharing/leaderboard/{group_id}/join",
            json={"invite_code": data["invite_code"]},
        )
        assert response.status_code == 200

        response = client.post(f"/api/v1/sharing/leaderboard/{group_id}/leave")
        assert response.status_code == 204

        app.dependency_overrides[get_current_user] = lambda: creator
        response = client.delete(f"/api/v1/sharing/leaderboard/{group_id}")
        assert response.status_code == 204

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Invite QR
# ---------------------------------------------------------------------------

def test_invite_qr_route():
    from salus.main import app

    with TestClient(app) as client:
        response = client.get("/sharing/connections/invite-qr?url=test")
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"


# ---------------------------------------------------------------------------
# Federation cache, notify, webfinger, access log, message signatures
# ---------------------------------------------------------------------------

def test_federated_measurement_cache_and_ttl():
    from salus.models.sharing import FederatedMeasurementCache

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    uow = SqlUnitOfWork(Session(engine))

    with uow:
        user = UserModel(username="bob", password_hash="hash")
        uow.users.add(user)
        uow.commit()
        bob_id = uid(user)

        metric_def = MetricDefinition(code="cache_steps", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric_def)
        uow.commit()
        metric_code = metric_def.code

    svc = SharingService.create(uow)

    with uow:
        cache_entry = FederatedMeasurementCache(
            owner_handle="@alice:remote.com",
            data_type="steps",
            date_str="2026-07-03",
            value_json='[{"value_numeric": 8200.0, "data_type": "steps"}]',
            fetched_at=datetime.now(timezone.utc),
        )
        uow.session.add(cache_entry)
        uow.commit()

    called_remote = False

    def mock_fetch_remote(handle, data_type, date_str):
        nonlocal called_remote
        called_remote = True
        return []

    svc._resolver._fetch_remote = mock_fetch_remote

    data = svc.resolve_and_fetch(bob_id, "@alice:remote.com", "steps", "2026-07-03")
    assert len(data) == 1
    assert data[0]["value_numeric"] == 8200.0
    assert not called_remote

    with uow:
        from sqlmodel import select
        from datetime import timedelta

        entry = uow.session.exec(select(FederatedMeasurementCache)).first()
        assert entry is not None
        entry.fetched_at = datetime.now(timezone.utc) - timedelta(minutes=20)
        uow.session.add(entry)
        uow.commit()

    svc.resolve_and_fetch(bob_id, "@alice:remote.com", "steps", "2026-07-03")
    assert called_remote


def test_federated_notify_update_route():
    from salus.main import app
    from salus.dependencies import get_session, get_sharing_service

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    uow = SqlUnitOfWork(Session(engine))

    with uow:
        user = UserModel(username="bob", password_hash="hash")
        uow.users.add(user)
        uow.commit()
        bob_id = uid(user)

        metric = MetricDefinition(code="notify_steps", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric)
        uow.commit()
        metric_code = metric.code

    svc = SharingService.create(uow)
    rel = svc.create_relationship(
        owner_id=bob_id, grantee_handle="@alice:remote.com",
        metric_code=metric_code,
    )

    with uow:
        db_rel = uow.sharing_relationships.get_by_id(rel.id)
        assert db_rel is not None
        db_rel.status = ConnectionStatus.ACTIVE
        uow.sharing_relationships.update(db_rel)
        uow.commit()

    app.dependency_overrides[get_session] = lambda: Session(engine)
    app.dependency_overrides[get_sharing_service] = lambda: svc

    token_hash = rel.api_token_hash

    def mock_fetch_remote(handle, data_type, date_str):
        return [{"value_numeric": 12000.0}]

    svc._resolver._fetch_remote = mock_fetch_remote

    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/federation/notify-update",
            json={"owner_handle": "@alice:remote.com", "data_type": "steps", "date": "2026-07-03"},
            headers={"Authorization": "Bearer invalid_hash"},
        )
        assert resp.status_code == 401

        resp = client.post(
            "/api/v1/federation/notify-update",
            json={"owner_handle": "@alice:remote.com", "data_type": "steps", "date": "2026-07-03"},
            headers={"Authorization": f"Bearer {token_hash}"},
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    app.dependency_overrides.clear()


def test_webfinger_and_actor_discovery():
    from salus.main import app
    from salus.dependencies import get_session, get_sharing_service

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    uow = SqlUnitOfWork(Session(engine))

    with uow:
        user = UserModel(username="bob", password_hash="hash")
        uow.users.add(user)
        uow.commit()
        uid(user)

    svc = SharingService.create(uow)

    app.dependency_overrides[get_session] = lambda: Session(engine)
    app.dependency_overrides[get_sharing_service] = lambda: svc

    with TestClient(app) as client:
        resp = client.get("/.well-known/webfinger", params={"resource": "invalid_scheme"})
        assert resp.status_code == 400

        resp = client.get("/.well-known/webfinger", params={"resource": "acct:alice@testserver"})
        assert resp.status_code == 404

        resp = client.get("/.well-known/webfinger", params={"resource": "acct:bob@testserver"})
        assert resp.status_code == 200
        jrd = resp.json()
        assert jrd["subject"] == "acct:bob@testserver"
        assert len(jrd["links"]) == 1
        assert jrd["links"][0]["rel"] == "self"
        actor_url = jrd["links"][0]["href"]
        assert "/api/v1/federation/actors/bob" in actor_url

        resp = client.get("/api/v1/federation/actors/bob")
        assert resp.status_code == 200
        profile = resp.json()
        assert profile["preferredUsername"] == "bob"
        assert profile["endpoints"]["sharing"].endswith("/api/v1/federation/sharing")

        resp = client.get("/api/v1/federation/actors/alice")
        assert resp.status_code == 404

    called_webfinger = False
    called_actor = False

    def mock_httpx_get(url, *args, **kwargs):
        nonlocal called_webfinger, called_actor
        if "/.well-known/webfinger" in url:
            called_webfinger = True

            class MockResponse:
                status_code = 200

                def json(self):
                    return {
                        "subject": "acct:alice@remote.com",
                        "links": [{"rel": "self", "href": "http://remote.com/api/v1/federation/actors/alice"}],
                    }

                def raise_for_status(self):
                    pass

            return MockResponse()
        elif "/actors/alice" in url:
            called_actor = True

            class MockResponse:
                status_code = 200

                def json(self):
                    return {
                        "preferredUsername": "alice",
                        "endpoints": {
                            "sharing": "http://remote.com/custom/sharing",
                            "accept": "http://remote.com/custom/accept",
                            "notify": "http://remote.com/custom/notify",
                        },
                    }

                def raise_for_status(self):
                    pass

            return MockResponse()
        raise ValueError(f"Unmocked URL: {url}")

    import httpx

    original_get = httpx.get
    httpx.get = mock_httpx_get

    try:
        endpoints = svc._resolve_remote_endpoints("@alice:remote.com")
        assert called_webfinger
        assert called_actor
        assert endpoints["sharing"] == "http://remote.com/custom/sharing"
        assert endpoints["accept"] == "http://remote.com/custom/accept"
        assert endpoints["notify"] == "http://remote.com/custom/notify"
    finally:
        httpx.get = original_get

    app.dependency_overrides.clear()


def test_federated_access_log():
    from salus.main import app
    from salus.dependencies import get_session, get_sharing_service, get_current_user

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    uow = SqlUnitOfWork(Session(engine))

    with uow:
        bob = UserModel(username="bob", password_hash="hash")
        uow.users.add(bob)
        uow.commit()
        bob_id = uid(bob)

        metric = MetricDefinition(code="access_log_steps", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric)
        uow.commit()
        metric_code = metric.code

    svc = SharingService.create(uow)
    rel = svc.create_relationship(
        owner_id=bob_id, grantee_handle="@alice:remote.com",
        metric_code=metric_code,
    )

    with uow:
        db_rel = uow.sharing_relationships.get_by_id(rel.id)
        assert db_rel is not None
        db_rel.status = ConnectionStatus.ACTIVE
        uow.sharing_relationships.update(db_rel)
        uow.commit()

    app.dependency_overrides[get_session] = lambda: Session(engine)
    app.dependency_overrides[get_sharing_service] = lambda: svc
    app.dependency_overrides[get_current_user] = lambda: bob

    with TestClient(app) as client:
        import hashlib

        raw_token = "some_raw_token"
        with uow:
            db_rel = uow.sharing_relationships.get_by_id(rel.id)
            assert db_rel is not None
            db_rel.api_token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
            uow.sharing_relationships.update(db_rel)
            uow.commit()

        resp = client.get(
            "/api/v1/federation/sharing",
            params={"owner_username": "bob", "data_type": "steps", "date": "2026-07-03"},
            headers={"Authorization": f"Bearer {raw_token}"},
        )
        assert resp.status_code == 200

        resp = client.get("/api/v1/federation/access-log")
        assert resp.status_code == 200
        logs = resp.json()["logs"]
        assert len(logs) == 1
        assert logs[0]["requester_handle"] == "@alice:remote.com"
        assert logs[0]["data_type"] == "steps"
        assert logs[0]["target_date"] == "2026-07-03"

    app.dependency_overrides.clear()


def test_federated_http_message_signatures():
    from salus.main import app
    from salus.dependencies import get_session, get_sharing_service

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    uow = SqlUnitOfWork(Session(engine))

    with uow:
        bob = UserModel(username="bob", password_hash="hash")
        uow.users.add(bob)
        uow.commit()
        bob_id = uid(bob)

        metric = MetricDefinition(code="sig_steps", name="Steps", unit="steps", source_data_type="steps")
        uow.metric_definitions.add(metric)
        uow.commit()
        metric_code = metric.code

    svc = SharingService.create(uow)
    rel = svc.create_relationship(
        owner_id=bob_id, grantee_handle="@alice:remote.com",
        metric_code=metric_code,
    )

    with uow:
        db_rel = uow.sharing_relationships.get_by_id(rel.id)
        assert db_rel is not None
        db_rel.status = ConnectionStatus.ACTIVE
        uow.sharing_relationships.update(db_rel)
        uow.commit()

    priv, pub = svc.get_instance_keys()
    assert priv.startswith("-----BEGIN PRIVATE KEY-----")
    assert pub.startswith("-----BEGIN PUBLIC KEY-----")

    def mock_resolve_actor_public_key(sender_handle):
        return pub

    svc._keys.resolve_actor_public_key = mock_resolve_actor_public_key

    url = "http://testserver/api/v1/federation/sharing?owner_username=bob&data_type=steps&date=2026-07-03"
    sig_headers = svc.sign_request(
        sender_handle="@alice:remote.com",
        method="GET",
        url_str=url,
    )

    assert "Signature" in sig_headers
    assert "Signature-Input" in sig_headers
    assert "X-Salus-Nonce" in sig_headers
    assert "X-Salus-Timestamp" in sig_headers

    app.dependency_overrides[get_session] = lambda: Session(engine)
    app.dependency_overrides[get_sharing_service] = lambda: svc

    with TestClient(app) as client:
        resp = client.get(
            "/api/v1/federation/sharing",
            params={"owner_username": "bob", "data_type": "steps", "date": "2026-07-03"},
            headers=sig_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    app.dependency_overrides.clear()
