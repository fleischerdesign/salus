import pytest
from salus.models.user import User
from salus.models.user_source_preference import UserSourcePreference
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.schemas.user_source_preference import MetricSourcePriorityItem
from salus.services.source_resolution import SourceResolutionService


def test_user_source_preference_repository(db_session):
    user = User(username="test_user", email="test@salus.local", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    uow = SqlUnitOfWork(db_session)
    repo = uow.user_source_preferences

    pref = UserSourcePreference(
        user_id=user.id,
        metric_code="sleep",
        source="oura",
        priority_rank=1,
        is_enabled=True,
    )
    repo.add(pref)
    db_session.commit()

    found = repo.find_by_user(user.id)
    assert len(found) == 1
    assert found[0].source == "oura"

    by_metric = repo.find_by_user_and_metric(user.id, "sleep")
    assert len(by_metric) == 1
    assert by_metric[0].priority_rank == 1

    single = repo.find_by_user_metric_source(user.id, "sleep", "oura")
    assert single is not None
    assert single.source == "oura"


def test_source_resolution_service(db_session):
    user = User(username="test_user_svc", email="test_svc@salus.local", password_hash="hash")
    db_session.add(user)
    db_session.commit()

    uow = SqlUnitOfWork(db_session)
    svc = SourceResolutionService(uow)

    items = [
        MetricSourcePriorityItem(source="oura", priority_rank=1, is_enabled=True),
        MetricSourcePriorityItem(source="apple_health", priority_rank=2, is_enabled=False),
    ]

    updated = svc.set_metric_preferences(user.id, "sleep", items)
    db_session.commit()

    assert len(updated) == 2
    assert updated[0].source == "oura"
    assert updated[1].is_enabled is False

    grouped = svc.get_user_preferences(user.id)
    assert "sleep" in grouped
    assert len(grouped["sleep"]) == 2


def test_source_preferences_api(authenticated_client):
    res = authenticated_client.get("/api/v1/settings/source-preferences")
    assert res.status_code == 200

    payload = [
        {"source": "oura", "priority_rank": 1, "is_enabled": True},
        {"source": "health_connect", "priority_rank": 2, "is_enabled": True},
    ]

    put_res = authenticated_client.put("/api/v1/settings/source-preferences/sleep", json=payload)
    assert put_res.status_code == 200
    data = put_res.json()
    assert len(data) == 2
    assert data[0]["source"] == "oura"

    get_res = authenticated_client.get("/api/v1/settings/source-preferences/sleep")
    assert get_res.status_code == 200
    assert len(get_res.json()) == 2
