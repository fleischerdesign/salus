import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from salus.database import engine
from salus.models import MetricType
from salus.models.measurement import Measurement
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services.open_science import OpenScienceService
from salus.schemas.open_science import OpenScienceSynthesizeRequest


@pytest.fixture
def clean_db():
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture
def auth_client():
    from salus.main import app
    import uuid

    username = f"science_user_{uuid.uuid4().hex[:6]}"
    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "password123"},
        )
        token = resp.json()["token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        yield client, username


def test_laplace_distribution_noise():
    service = OpenScienceService(None)  # type: ignore
    
    # Epsilon = 1.0, scale = 100.0. Noise should be non-zero
    noises = [service.sample_laplace(0.0, 100.0) for _ in range(50)]
    assert any(n != 0.0 for n in noises)
    
    # Epsilon = infinite (scale = 0.0). Noise must be exactly 0.0
    zero_noises = [service.sample_laplace(0.0, 0.0) for _ in range(10)]
    assert all(n == 0.0 for n in zero_noises)


def test_demographic_binning():
    class MockUOW:
        def __enter__(self): return self
        def __exit__(self, exc_type, exc_val, exc_tb): pass
        @property
        def metric_types(self):
            class R:
                def find_all(self, uid): return []
            return R()

    service = OpenScienceService(MockUOW())  # type: ignore
    
    # Test age grouping
    req_age = OpenScienceSynthesizeRequest(
        metrics=["steps"],
        epsilon=1.0,
        include_demographics=True,
        user_birth_year=1990
    )
    res = service.synthesize(user_id=1, req=req_age)
    
    current_year = datetime.now().year
    expected_age = current_year - 1990
    expected_bin = f"{expected_age // 10 * 10}-{expected_age // 10 * 10 + 9}"
    
    assert res["demographics"]["age_group"] == expected_bin

    # Test weight grouping (e.g. 73.4 -> 70-74 kg)
    req_weight = OpenScienceSynthesizeRequest(
        metrics=["steps"],
        epsilon=1.0,
        include_demographics=True,
        user_weight_kg=73.4
    )
    res2 = service.synthesize(user_id=1, req=req_weight)
    assert res2["demographics"]["weight_group"] == "70-74 kg"


def test_synthesis_and_api_route(clean_db, auth_client):
    client, username = auth_client
    # 1. Create a metric type and some measurements in DB
    from sqlmodel import Session
    session = Session(engine)
    uow = SqlUnitOfWork(session)
    
    with uow:
        # Find first user
        user = uow.users.get_by_username(username)
        assert user is not None
        user_id = user.id
        
        # Create metric type "steps" or use existing
        mt = uow.metric_types.find_by_name_and_user("steps", user_id)
        if not mt:
            mt = MetricType(name="steps", type="number", user_id=user_id)
            uow.metric_types.add(mt)
            uow.commit()
        
        # Add 3 days of measurements
        for i in range(3):
            # Timestamp goes back day-by-day
            ts = datetime.now(timezone.utc) - timedelta(days=i)
            m = Measurement(
                user_id=user_id,
                metric_type_id=mt.id,  # type: ignore
                value_numeric=10000.0 + (i * 1000),
                start_time=ts
            )
            uow.measurements.add(m)
        uow.commit()

    # 2. Call Synthesis API route
    payload = {
        "metrics": ["steps"],
        "weeks": 2,
        "epsilon": 1.0,
        "include_demographics": True,
        "user_birth_year": 1988,
        "user_weight_kg": 84.5
    }
    
    resp = client.post("/api/v1/open-science/synthesize", json=payload)
    assert resp.status_code == 200
    res = resp.json()
    
    assert "records" in res
    assert len(res["records"]) > 0
    assert "week" in res["records"][0]
    assert "steps" in res["records"][0]
    # Steps should be near 11000 average (but with Laplace noise added)
    assert res["records"][0]["steps"] >= 0.0
