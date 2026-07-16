import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from salus.database import Session, engine
from salus.models.measurement import Measurement
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services.circadian import CircadianService
from salus.schemas.circadian import CircadianProfileCreate


@pytest.fixture
def clean_db():
    yield


@pytest.fixture
def auth_client(client):
    import uuid

    username = f"circadian_user_{uuid.uuid4().hex[:6]}"
    resp = client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "password123"},
    )
    token = resp.json()["token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    yield client, username


def test_noaa_solar_calculator_berlin():
    service = CircadianService(None)  # type: ignore

    date = datetime(2026, 3, 20)
    solar = service.calculate_solar_times(date, 52.52, 13.40, 1.0)

    assert "06:" in solar["sunrise"]
    assert "18:" in solar["sunset"]
    assert "12:" in solar["solar_noon"]


def test_circadian_profile_crud(clean_db, auth_client):
    client, username = auth_client
    test_engine = client.app.state.engine
    session = Session(test_engine)
    uow = SqlUnitOfWork(session)
    service = CircadianService(uow)

    with uow:
        user = uow.users.get_by_username(username)
        assert user is not None
        user_id = user.id

    profile = service.get_or_create_profile(user_id)
    assert profile.latitude == 52.52
    assert profile.configured_chronotype == "intermediate"

    data = CircadianProfileCreate(
        latitude=48.8566,
        longitude=2.3522,
        timezone_offset_hours=1.0,
        configured_chronotype="morning_lark",
    )
    saved = service.save_profile(user_id, data)
    assert saved.latitude == 48.8566
    assert saved.configured_chronotype == "morning_lark"


def test_circadian_advisor_engine(clean_db, auth_client):
    client, username = auth_client
    test_engine = client.app.state.engine
    session = Session(test_engine)
    uow = SqlUnitOfWork(session)
    service = CircadianService(uow)

    with uow:
        user = uow.users.get_by_username(username)
        assert user is not None
        user_id = user.id

        ts_start = datetime.now() - timedelta(days=1)
        sleep_start = datetime(ts_start.year, ts_start.month, ts_start.day, 23, 30)
        sleep_end = sleep_start + timedelta(hours=8)

        m = Measurement(
            user_id=user_id,
            metric_code="sleep",
            value_text="Sleep entry",
            start_time=sleep_start,
            end_time=sleep_end,
        )
        uow.measurements.add(m)
        uow.commit()

    advice = service.calculate_advice(user_id)
    assert advice.sleep_window["actual_onset"] == "23:30"
    assert advice.sleep_window["actual_offset"] == "07:30"
    assert advice.alignment_score > 0
    assert len(advice.light_advice) == 2
    assert advice.eating_window["start"] != ""


def test_circadian_profile_route(clean_db, auth_client):
    client, _ = auth_client
    resp = client.post(
        "/api/v1/circadian/profile",
        json={
            "latitude": 37.7749,
            "longitude": -122.4194,
            "timezone_offset_hours": -8.0,
            "configured_chronotype": "night_owl",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["latitude"] == 37.7749
    assert data["longitude"] == -122.4194
    assert data["timezone_offset_hours"] == -8.0
    assert data["configured_chronotype"] == "night_owl"
    assert "id" in data
    assert "user_id" in data


def test_circadian_profile_route_invalid_data(clean_db, auth_client):
    client, _ = auth_client
    resp = client.post(
        "/api/v1/circadian/profile",
        json={"latitude": "not-a-number", "timezone_offset_hours": 1.0},
    )
    assert resp.status_code == 422

