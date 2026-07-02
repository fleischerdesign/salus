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
from salus.exceptions import NotFoundError, ConflictError


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
        owner_id = owner.id
        grantee_id = grantee.id

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
        owner_id = owner.id
        grantee_id = grantee.id

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
        owner_id = owner.id

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
        owner_id = owner.id

        m1 = MetricType(name="Steps", unit="steps", data_type=DataType.NUMBER, user_id=owner_id, is_system=True, source_data_type="steps")
        m2 = MetricType(name="Weight", unit="kg", data_type=DataType.NUMBER, user_id=owner_id, is_system=True, source_data_type="weight")
        uow.metric_types.add(m1)
        uow.metric_types.add(m2)
        uow.commit()
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
                "metric_type_ids": [m1_id, m2_id],
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

