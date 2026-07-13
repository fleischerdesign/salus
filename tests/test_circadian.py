import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlmodel import SQLModel

from salus.database import Session, engine
from salus.models import MetricType
from salus.models.measurement import Measurement
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
    session = Session(engine)
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
    session = Session(engine)
    uow = SqlUnitOfWork(session)
    service = CircadianService(uow)

    with uow:
        user = uow.users.get_by_username(username)
        assert user is not None
        user_id = user.id

        mt = uow.metric_types.find_by_name_and_user("Sleep", user_id)
        if not mt:
            mt = MetricType(name="Sleep", type="text", user_id=user_id)
            uow.metric_types.add(mt)
            uow.commit()

        ts_start = datetime.now() - timedelta(days=1)
        sleep_start = datetime(ts_start.year, ts_start.month, ts_start.day, 23, 30)
        sleep_end = sleep_start + timedelta(hours=8)

        m = Measurement(
            user_id=user_id,
            metric_type_id=mt.id,  # type: ignore
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

