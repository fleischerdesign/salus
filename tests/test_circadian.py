import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, select

from salus.database import Session, engine
from salus.models.user import User
from salus.models.circadian import CircadianProfile
from salus.models.measurement import Measurement
from salus.models import MetricType
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services.circadian import CircadianService
from salus.schemas.circadian import CircadianProfileCreate


@pytest.fixture
def clean_db():
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture
def auth_client():
    from salus.main import app
    import uuid
    username = f"circadian_user_{uuid.uuid4().hex[:6]}"
    with TestClient(app) as client:
        client.post("/auth/register", data={"username": username, "password": "password123"})
        client.post("/auth/login", data={"username": username, "password": "password123"})
        yield client, username


def test_noaa_solar_calculator_berlin():
    service = CircadianService(None)  # type: ignore
    
    # Test solar calculations for Berlin (52.52 lat, 13.40 lon, UTC+1) on Spring Equinox (March 20, 2026)
    date = datetime(2026, 3, 20)
    solar = service.calculate_solar_times(date, 52.52, 13.40, 1.0)
    
    # Sunrise should be around 06:10 local time
    # Sunset should be around 18:20 local time
    assert "06:" in solar["sunrise"]
    assert "18:" in solar["sunset"]
    assert "12:" in solar["solar_noon"]


def test_circadian_profile_crud(clean_db, auth_client):
    client, username = auth_client
    session = Session(engine)
    uow = SqlUnitOfWork(session)
    service = CircadianService(uow)
    
    with uow:
        user = uow.users.get_by_username(username)
        assert user is not None
        user_id = user.id

    # 1. Fetch defaults (should auto-create profile)
    profile = service.get_or_create_profile(user_id)
    assert profile.latitude == 52.52
    assert profile.configured_chronotype == "intermediate"

    # 2. Save custom profile
    data = CircadianProfileCreate(
        latitude=48.8566,  # Paris
        longitude=2.3522,
        timezone_offset_hours=1.0,
        configured_chronotype="morning_lark"
    )
    saved = service.save_profile(user_id, data)
    assert saved.latitude == 48.8566
    assert saved.configured_chronotype == "morning_lark"


def test_circadian_advisor_engine(clean_db, auth_client):
    client, username = auth_client
    session = Session(engine)
    uow = SqlUnitOfWork(session)
    service = CircadianService(uow)
    
    with uow:
        user = uow.users.get_by_username(username)
        assert user is not None
        user_id = user.id
        
        # Seed a "Sleep" metric type and log sleep entries
        mt = uow.metric_types.find_by_name_and_user("Sleep", user_id)
        if not mt:
            mt = MetricType(name="Sleep", type="text", user_id=user_id)
            uow.metric_types.add(mt)
            uow.commit()

        # Add sleep log (onset 23:30, offset 07:30)
        ts_start = datetime.now() - timedelta(days=1)
        # Sleep from 23:30 to 07:30 next day
        sleep_start = datetime(ts_start.year, ts_start.month, ts_start.day, 23, 30)
        sleep_end = sleep_start + timedelta(hours=8)
        
        m = Measurement(
            user_id=user_id,
            metric_type_id=mt.id,  # type: ignore
            value_text="Sleep entry",
            start_time=sleep_start,
            end_time=sleep_end
        )
        uow.measurements.add(m)
        uow.commit()

    # Calculate advisor recommendations
    advice = service.calculate_advice(user_id)
    assert advice.sleep_window["actual_onset"] == "23:30"
    assert advice.sleep_window["actual_offset"] == "07:30"
    assert advice.alignment_score > 0
    assert len(advice.light_advice) == 2
    assert advice.eating_window["start"] != ""


def test_circadian_routes(clean_db, auth_client):
    client, username = auth_client

    # 1. Update profile via POST form
    form_payload = {
        "latitude": 37.7749,  # SF
        "longitude": -122.4194,
        "timezone_offset_hours": -8.0,
        "configured_chronotype": "night_owl"
    }
    resp = client.post("/circadian/profile", data=form_payload, follow_redirects=False)
    assert resp.status_code == 303  # Redirects back to dashboard

    # 2. Request dashboard HTML
    get_resp = client.get("/circadian")
    assert get_resp.status_code == 200
    assert "Circadian &amp; Light Advisor" in get_resp.text
    # Verify coordinates rendered in page
    assert "37.7749" in get_resp.text
