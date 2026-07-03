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
from salus.models.sharing import SharingRelationship
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


def test_sharing_service_local_and_remote_creation(session: Session):
    uow = SqlUnitOfWork(session)
    service = SharingService(uow)

    with uow:
        # Create users
        owner = UserModel(username="owner", password_hash="hash")
        grantee = UserModel(username="grantee", password_hash="hash")
        uow.users.add(owner)
        uow.users.add(grantee)
        uow.commit()
        owner_id = uid(owner)
        grantee_id = uid(grantee)

        # Seed metric
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

    # 1. Create local relationship (grantee exists)
    rel_local = service.create_relationship(
        owner_id=owner_id,
        grantee_handle="@grantee",
        metric_type_id=metric_id,
    )
    assert rel_local.id is not None
    assert rel_local.grantee_handle == "@grantee"
    assert rel_local.aggregation_level == "daily_summary"

    # 2. Reject duplicates
    with pytest.raises(ConflictError):
        service.create_relationship(
            owner_id=owner_id,
            grantee_handle="@grantee",
            metric_type_id=metric_id,
        )

    # 3. Create remote relationship (no local existence check required)
    rel_remote = service.create_relationship(
        owner_id=owner_id,
        grantee_handle="@alice:remote-server.com",
        metric_type_id=metric_id,
    )
    assert rel_remote.id is not None
    assert rel_remote.grantee_handle == "@alice:remote-server.com"


def test_sharing_resolution_and_aggregation(session: Session):
    uow = SqlUnitOfWork(session)
    service = SharingService(uow)

    with uow:
        # Create users
        owner = UserModel(username="owner", password_hash="hash")
        grantee = UserModel(username="grantee", password_hash="hash")
        uow.users.add(owner)
        uow.users.add(grantee)
        uow.commit()
        owner_id = uid(owner)
        grantee_id = uid(grantee)

        # Seed metric
        metric = MetricType(
            name="Steps",
            unit="steps",
            data_type=DataType.NUMBER,
            user_id=owner_id,
            is_system=True,
            source_data_type="steps",
        )
        uow.metric_types.add(metric)
        uow.commit()
        assert metric.id is not None
        metric_id = metric.id

        # Seed measurements (two step entries on 2026-07-02: 5000 and 3000 steps)
        t_utc = datetime(2026, 7, 2, 10, 0, tzinfo=timezone.utc)
        m1 = Measurement(
            user_id=owner_id,
            metric_type_id=metric_id,
            data_type="steps",
            value_numeric=5000.0,
            start_time=t_utc,
            source="manual",
            external_id="m1"
        )
        m2 = Measurement(
            user_id=owner_id,
            metric_type_id=metric_id,
            data_type="steps",
            value_numeric=3000.0,
            start_time=t_utc,
            source="manual",
            external_id="m2"
        )
        uow.measurements.add(m1)
        uow.measurements.add(m2)
        uow.commit()

    # Before sharing: Access should raise PermissionError
    with pytest.raises(PermissionError):
        service.resolve_and_fetch(
            requester_id=grantee_id,
            owner_handle="@owner",
            data_type="steps",
            date_str="2026-07-02"
        )

    # Share with daily_summary level
    service.create_relationship(
        owner_id=owner_id,
        grantee_handle="@grantee",
        metric_type_id=metric_id,
        aggregation_level="daily_summary"
    )

    # Read daily summary (should return 1 entry with value 8000.0)
    data = service.resolve_and_fetch(
        requester_id=grantee_id,
        owner_handle="@owner",
        data_type="steps",
        date_str="2026-07-02"
    )
    assert len(data) == 1
    assert data[0]["value_numeric"] == 8000.0
    assert data[0]["source"] == "summary"

    # Deactivate and check error
    with uow:
        rel = uow.sharing_relationships.find_by_owner(owner_id)[0]
        assert rel.id is not None
        service.deactivate_relationship(owner_id, rel.id)

    with pytest.raises(PermissionError):
        service.resolve_and_fetch(
            requester_id=grantee_id,
            owner_handle="@owner",
            data_type="steps",
            date_str="2026-07-02"
        )


def test_federated_api_endpoint(session: Session):
    # Setup App dependencies
    from salus.main import app, templates
    from salus.dependencies import get_session

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    app.dependency_overrides[get_session] = lambda: Session(engine)

    uow = SqlUnitOfWork(Session(engine))
    with uow:
        # Create users
        owner = UserModel(username="owner", password_hash="hash")
        uow.users.add(owner)
        uow.commit()
        owner_id = uid(owner)

        # Seed metric
        metric = MetricType(
            name="Steps",
            unit="steps",
            data_type=DataType.NUMBER,
            user_id=owner_id,
            is_system=True,
            source_data_type="steps",
        )
        uow.metric_types.add(metric)
        uow.commit()
        assert metric.id is not None
        metric_id = metric.id

        # Seed measurement
        m = Measurement(
            user_id=owner_id,
            metric_type_id=metric_id,
            data_type="steps",
            value_numeric=9500.0,
            start_time=datetime(2026, 7, 2, 10, 0, tzinfo=timezone.utc),
            source="manual",
            external_id="m-api"
        )
        uow.measurements.add(m)
        uow.commit()

    # Share relationship
    sharing_svc = SharingService(uow)
    rel = sharing_svc.create_relationship(
        owner_id=owner_id,
        grantee_handle="@alice:external-server.com",
        metric_type_id=metric_id,
        aggregation_level="raw"
    )
    token = rel.api_token_hash

    # Test HTTP Client
    with TestClient(app) as client:
        # 1. Access with invalid token -> 401
        response = client.get(
            "/api/v1/federation/sharing",
            params={"owner_username": "owner", "data_type": "steps", "date": "2026-07-02"},
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401

        # 2. Access with valid token -> 200
        response = client.get(
            "/api/v1/federation/sharing",
            params={"owner_username": "owner", "data_type": "steps", "date": "2026-07-02"},
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        res_data = response.json()
        assert res_data["status"] == "ok"
        assert len(res_data["data"]) == 1
        assert res_data["data"][0]["value_numeric"] == 9500.0

    app.dependency_overrides.clear()


def test_sharing_post_route():
    from salus.main import app
    from salus.dependencies import get_session, get_current_user

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    
    uow = SqlUnitOfWork(Session(engine))
    with uow:
        owner = UserModel(username="owner", password_hash="hash")
        uow.users.add(owner)
        uow.commit()
        owner_id = uid(owner)

        m1 = MetricType(name="Steps", unit="steps", data_type=DataType.NUMBER, user_id=owner_id, is_system=True, source_data_type="steps")
        m2 = MetricType(name="Weight", unit="kg", data_type=DataType.NUMBER, user_id=owner_id, is_system=True, source_data_type="weight")
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
        # Post request with multiple metrics selected and different aggregation levels
        response = client.post(
            "/sharing",
            data={
                "grantee_handle": "@grantee:external.com",
                "metric_type_ids": [str(m1_id), str(m2_id)],
                f"aggregation_level_{m1_id}": "raw",
                f"aggregation_level_{m2_id}": "daily_summary"
            },
            follow_redirects=False
        )
        # Should redirect back to /sharing
        assert response.status_code == 303
        
        # Verify both sharing relationships exist with correct levels
        with uow:
            rels = uow.sharing_relationships.find_by_owner(owner_id)
            assert len(rels) == 2
            assert {r.metric_type_id for r in rels} == {m1_id, m2_id}
            
            m1_rel = next(r for r in rels if r.metric_type_id == m1_id)
            m2_rel = next(r for r in rels if r.metric_type_id == m2_id)
            assert m1_rel.aggregation_level == "raw"
            assert m2_rel.aggregation_level == "daily_summary"

    app.dependency_overrides.clear()


def test_sharing_expiration_and_invalid_date(session: Session):
    from datetime import timedelta
    uow = SqlUnitOfWork(session)
    service = SharingService(uow)

    with uow:
        # Create users
        owner = UserModel(username="owner", password_hash="hash")
        grantee = UserModel(username="grantee", password_hash="hash")
        uow.users.add(owner)
        uow.users.add(grantee)
        uow.commit()
        owner_id = uid(owner)
        grantee_id = uid(grantee)

        # Seed metric
        metric = MetricType(
            name="Steps",
            unit="steps",
            data_type=DataType.NUMBER,
            user_id=owner_id,
            is_system=True,
            source_data_type="steps",
        )
        uow.metric_types.add(metric)
        uow.commit()
        assert metric.id is not None
        metric_id = metric.id

        # Seed measurement on current date
        m = Measurement(
            user_id=owner_id,
            metric_type_id=metric_id,
            data_type="steps",
            value_numeric=12000.0,
            start_time=datetime.now(timezone.utc),
            source="manual",
            external_id="m-exp"
        )
        uow.measurements.add(m)
        uow.commit()

    # 1. Share with negative expiration days (already expired in the past)
    rel = service.create_relationship(
        owner_id=owner_id,
        grantee_handle="@grantee",
        metric_type_id=metric_id,
        expiration_days=-1,  # Expired yesterday
    )
    assert rel.id is not None

    # Access should raise PermissionError due to expiration
    with pytest.raises(PermissionError):
        service.resolve_and_fetch(
            requester_id=grantee_id,
            owner_handle="@owner",
            data_type="steps",
            date_str=datetime.now(timezone.utc).strftime("%Y-%m-%d")
        )

    # Reactivate relationship by removing expiration date
    with uow:
        db_rel = uow.sharing_relationships.get_by_id(rel.id)
        assert db_rel is not None
        db_rel.expiration_date = None
        uow.sharing_relationships.update(db_rel)
        uow.commit()

    # Access should succeed now
    res = service.resolve_and_fetch(
        requester_id=grantee_id,
        owner_handle="@owner",
        data_type="steps",
        date_str=datetime.now(timezone.utc).strftime("%Y-%m-%d")
    )
    assert len(res) == 1
    assert res[0]["value_numeric"] == 12000.0

    # 2. Test invalid date fallback (e.g. passing "invalid-date-string")
    # It should fall back to current date and find the measurement
    res_fallback = service.resolve_and_fetch(
        requester_id=grantee_id,
        owner_handle="@owner",
        data_type="steps",
        date_str="invalid-date-string"
    )
    assert len(res_fallback) == 1
    assert res_fallback[0]["value_numeric"] == 12000.0


def test_leaderboard_service_crud_and_logic(session: Session):
    uow = SqlUnitOfWork(session)
    service = LeaderboardService(uow)
    sharing_svc = SharingService(uow)

    with uow:
        creator = UserModel(username="creator", password_hash="hash")
        invitee = UserModel(username="invitee", password_hash="hash")
        uow.users.add(creator)
        uow.users.add(invitee)
        uow.commit()
        creator_id = uid(creator)
        invitee_id = uid(invitee)

        # Seed steps metric for both
        metric_c = MetricType(
            name="Steps",
            unit="steps",
            data_type=DataType.NUMBER,
            user_id=creator_id,
            is_system=True,
            source_data_type="steps",
        )
        metric_i = MetricType(
            name="Steps",
            unit="steps",
            data_type=DataType.NUMBER,
            user_id=invitee_id,
            is_system=True,
            source_data_type="steps",
        )
        uow.metric_types.add(metric_c)
        uow.metric_types.add(metric_i)
        uow.commit()
        assert metric_c.id is not None
        assert metric_i.id is not None
        metric_c_id = metric_c.id
        metric_i_id = metric_i.id

    # 1. Create a leaderboard challenge group
    group = service.create_group(
        creator_id=creator_id,
        name="Step Challenge",
        metric_type_code="steps",
        time_frame="weekly",
    )
    assert group.id is not None
    assert group.name == "Step Challenge"
    assert group.creator_id == creator_id
    assert group.invite_code is not None
    group_id = group.id

    # 2. Try to join without connection -> PermissionError
    with pytest.raises(PermissionError) as exc_info:
        service.join_by_code(invitee_id, group.invite_code)
    assert "You must be connected" in str(exc_info.value)

    # 3. Establish sharing connection (invitee shares with creator)
    sharing_svc.create_relationship(
        owner_id=invitee_id,
        grantee_handle="@creator",
        metric_type_id=metric_i_id,
        aggregation_level="daily_summary"
    )

    # Now join should succeed
    joined_group = service.join_by_code(invitee_id, group.invite_code)
    assert joined_group.id == group_id

    # Try to join again -> ConflictError
    with pytest.raises(ConflictError):
        service.join_by_code(invitee_id, group.invite_code)

    # 4. Get rankings before measurements
    rankings_data = service.get_group_rankings(group_id, creator_id)
    assert rankings_data["group"].id == group_id
    assert len(rankings_data["rankings"]) == 2
    assert rankings_data["rankings"][0]["score"] == 0.0

    # 5. Add measurements to both users
    with uow:
        # Creator measurement
        t_utc = datetime.now(timezone.utc)
        m_creator = Measurement(
            user_id=creator_id,
            metric_type_id=metric_c_id,
            data_type="steps",
            value_numeric=10000.0,
            start_time=t_utc,
            source="manual",
            external_id="m_creator"
        )
        # Invitee measurement
        m_invitee = Measurement(
            user_id=invitee_id,
            metric_type_id=metric_i_id,
            data_type="steps",
            value_numeric=15000.0,
            start_time=t_utc,
            source="manual",
            external_id="m_invitee"
        )
        uow.measurements.add(m_creator)
        uow.measurements.add(m_invitee)
        uow.commit()

    # Get rankings again -> invitee should be 1st with score 15000.0, creator 2nd with 10000.0
    rankings_data = service.get_group_rankings(group_id, creator_id)
    rankings = rankings_data["rankings"]
    assert rankings[0]["username"] == "invitee"
    assert rankings[0]["score"] == 15000.0
    assert rankings[1]["username"] == "creator"
    assert rankings[1]["score"] == 10000.0

    # 6. Invitee leaves the group
    service.leave_group(invitee_id, group_id)
    
    # Rankings should only contain creator now
    rankings_data = service.get_group_rankings(group_id, creator_id)
    assert len(rankings_data["rankings"]) == 1
    assert rankings_data["rankings"][0]["username"] == "creator"

    # Try leaving again -> NotFoundError
    with pytest.raises(NotFoundError):
        service.leave_group(invitee_id, group_id)

    # 7. Non-creator trying to delete group -> PermissionError
    with pytest.raises(PermissionError):
        service.delete_group(invitee_id, group_id)

    # Delete group by creator
    service.delete_group(creator_id, group_id)

    # Fetching rankings of deleted group -> NotFoundError
    with pytest.raises(NotFoundError):
        service.get_group_rankings(group_id, creator_id)


def test_leaderboard_routes():
    from salus.main import app
    from salus.dependencies import get_session, get_current_user

    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
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
            name="Steps",
            unit="steps",
            data_type=DataType.NUMBER,
            user_id=invitee_id,
            is_system=True,
            source_data_type="steps",
        )
        uow.metric_types.add(metric_i)
        uow.commit()
        assert metric_i.id is not None
        metric_i_id = metric_i.id

    app.dependency_overrides[get_session] = lambda: Session(engine)
    
    with TestClient(app) as client:
        # 1. Access leaderboard page for creator
        app.dependency_overrides[get_current_user] = lambda: creator
        response = client.get("/sharing/leaderboard")
        assert response.status_code == 200
        assert "Step Challenge" not in response.text  # No groups yet

        # 2. Create a challenge group via POST
        response = client.post(
            "/sharing/leaderboard/create",
            data={
                "name": "Step Challenge 2026",
                "metric_type_code": "steps",
                "time_frame": "weekly",
            },
            follow_redirects=False
        )
        # Should redirect to detail page of created group
        assert response.status_code == 303
        redirect_url = response.headers["location"]
        assert "/sharing/leaderboard/" in redirect_url
        group_id = int(redirect_url.split("/")[-1])

        # Verify details page
        response = client.get(f"/sharing/leaderboard/{group_id}")
        assert response.status_code == 200
        assert "Step Challenge 2026" in response.text
        assert "creator" in response.text

        # Fetch invite code from DB
        with uow:
            group = uow.leaderboard_groups.get_by_id(group_id)
            assert group is not None
            invite_code = group.invite_code

        # 3. Invitee tries to join without connection
        app.dependency_overrides[get_current_user] = lambda: invitee
        response = client.post(
            "/sharing/leaderboard/join",
            data={"invite_code": invite_code},
            follow_redirects=False
        )
        assert response.status_code == 303
        assert "error=" in response.headers["location"]

        # Invitee accesses detail page before joining -> redirected back with error
        response = client.get(f"/sharing/leaderboard/{group_id}", follow_redirects=False)
        assert response.status_code == 303

        # Create connection so invitee can join
        sharing_svc = SharingService(uow)
        sharing_svc.create_relationship(
            owner_id=invitee_id,
            grantee_handle="@creator",
            metric_type_id=metric_i_id,
            aggregation_level="daily_summary"
        )

        # Now try to join again via POST
        response = client.post(
            "/sharing/leaderboard/join",
            data={"invite_code": invite_code},
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == f"/sharing/leaderboard/{group_id}"

        # Now invitee gets 200 on detail page
        response = client.get(f"/sharing/leaderboard/{group_id}")
        assert response.status_code == 200
        assert "Step Challenge 2026" in response.text

        # 4. Invitee leaves the challenge
        response = client.post(
            f"/sharing/leaderboard/{group_id}/leave",
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/sharing/leaderboard"

        # 5. Creator deletes the group
        app.dependency_overrides[get_current_user] = lambda: creator
        response = client.post(
            f"/sharing/leaderboard/{group_id}/delete",
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/sharing/leaderboard"

    app.dependency_overrides.clear()
