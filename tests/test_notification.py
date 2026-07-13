import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from salus.exceptions import NotFoundError
from salus.models.user import User
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services._helpers import uid
from salus.services.notification import NotificationService


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
def seeded_user(session: Session):
    uow = SqlUnitOfWork(session)
    with uow:
        user = User(username="alice", password_hash="hash", email="alice@salus.local")
        uow.users.add(user)
        uow.commit()
        user_id = uid(user)
    return {"uow": uow, "user_id": user_id}


def test_create_notification(seeded_user):
    uow = seeded_user["uow"]
    user_id = seeded_user["user_id"]
    svc = NotificationService(uow)

    notif = svc.create_notification(user_id, "Test Title", "Test Message", "system")
    assert notif.id is not None
    assert notif.user_id == user_id
    assert notif.title == "Test Title"
    assert notif.message == "Test Message"
    assert notif.category == "system"
    assert notif.is_read is False


def test_create_notification_user_not_found(seeded_user):
    uow = seeded_user["uow"]
    svc = NotificationService(uow)

    with pytest.raises(NotFoundError):
        svc.create_notification(999, "Title", "Message")


def test_get_unread_and_all(seeded_user):
    uow = seeded_user["uow"]
    user_id = seeded_user["user_id"]
    svc = NotificationService(uow)

    svc.create_notification(user_id, "N1", "Msg1", "system")
    svc.create_notification(user_id, "N2", "Msg2", "challenge")

    all_notifs = svc.get_all(user_id)
    assert len(all_notifs) == 2

    unread = svc.get_unread(user_id)
    assert len(unread) == 2


def test_mark_as_read(seeded_user):
    uow = seeded_user["uow"]
    user_id = seeded_user["user_id"]
    svc = NotificationService(uow)

    notif = svc.create_notification(user_id, "N1", "Msg1", "system")
    assert notif.is_read is False

    read_notif = svc.mark_as_read(user_id, notif.id)
    assert read_notif.is_read is True

    unread = svc.get_unread(user_id)
    assert len(unread) == 0


def test_mark_all_as_read(seeded_user):
    uow = seeded_user["uow"]
    user_id = seeded_user["user_id"]
    svc = NotificationService(uow)

    svc.create_notification(user_id, "N1", "Msg1", "system")
    svc.create_notification(user_id, "N2", "Msg2", "challenge")

    svc.mark_all_as_read(user_id)

    unread = svc.get_unread(user_id)
    assert len(unread) == 0


class TestNotificationRoutes:
    def test_notifications_requires_auth(self, client):
        response = client.get("/api/v1/notification", follow_redirects=False)
        assert response.status_code in (401, 403)

    def test_notifications_list_empty(self, authenticated_client):
        response = authenticated_client.get("/api/v1/notification")
        assert response.status_code == 200
        assert response.json() == []

    def test_notifications_count(self, authenticated_client):
        response = authenticated_client.get("/api/v1/notification")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_mark_all_read(self, authenticated_client):
        response = authenticated_client.post("/api/v1/notifications/read-all")
        assert response.status_code == 204
