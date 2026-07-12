import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient

from salus.config import settings
from sqlmodel import select
from salus.database import Session, engine
from salus.models.user import User
from salus.repositories.unit_of_work import SqlUnitOfWork
from salus.services.asymmetric_share import AsymmetricShareService
from salus.schemas.asymmetric_share import ShareRecipientCreate, AsymmetricShareCreate


@pytest.fixture
def clean_db():
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
    yield
    # We do not drop to preserve test speed in sqlite memory, but since it's sqlite we can just yield


@pytest.fixture
def auth_client():
    from salus.main import app
    import uuid

    username = f"alice_asym_{uuid.uuid4().hex[:6]}"
    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/auth/register",
            json={"username": username, "password": "password123"},
        )
        token = resp.json()["token"]
        client.headers = {"Authorization": f"Bearer {token}"}
        yield client


def test_recipient_crud_and_asymmetric_share_flow(clean_db, auth_client):
    # 1. Create a recipient
    recipient_data = {
        "name": "Dr. House",
        "public_key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAv1..."
    }
    resp = auth_client.post("/api/v1/shares/asymmetric/recipients", json=recipient_data)
    assert resp.status_code == 201
    recipient = resp.json()
    assert recipient["name"] == "Dr. House"
    assert recipient["public_key"] == recipient_data["public_key"]

    # 2. List recipients
    list_resp = auth_client.get("/api/v1/shares/asymmetric/recipients")
    assert list_resp.status_code == 200
    recipients = list_resp.json()
    assert len(recipients) == 1
    assert recipients[0]["name"] == "Dr. House"

    # 3. Create asymmetric share
    share_data = {
        "recipient_id": recipient["id"],
        "encrypted_data": "base64-payload-here",
        "encrypted_key": "base64-aes-key-here",
        "expires_in_hours": 12
    }
    share_resp = auth_client.post("/api/v1/shares/asymmetric", json=share_data)
    assert share_resp.status_code == 201
    share = share_resp.json()
    assert share["encrypted_data"] == "base64-payload-here"
    assert share["expires_at"] is not None

    # 4. Fetch share publicly (No Auth Cookie)
    public_client = TestClient(auth_client.app)  # Anonymous client
    get_resp = public_client.get(f"/api/v1/shares/asymmetric/{share['id']}")
    assert get_resp.status_code == 200
    public_share = get_resp.json()
    assert public_share["encrypted_data"] == "base64-payload-here"

    # 5. Delete share
    del_resp = auth_client.delete(f"/api/v1/shares/asymmetric/{share['id']}")
    assert del_resp.status_code == 204

    # Verify deleted
    get_resp = public_client.get(f"/api/v1/shares/asymmetric/{share['id']}")
    assert get_resp.status_code == 404


def test_asymmetric_share_expiration(clean_db, auth_client):
    # Setup recipient
    recipient_data = {
        "name": "Dr. Watson",
        "public_key": " WatsonPublicRSAKeyString"
    }
    r_resp = auth_client.post("/api/v1/shares/asymmetric/recipients", json=recipient_data)
    recipient = r_resp.json()

    # Create share with expired time (or mock the DB entry)
    session = Session(engine)
    uow = SqlUnitOfWork(session)
    service = AsymmetricShareService(uow)

    # Resolve test user id
    with uow:
        user = uow.session.exec(select(User)).first()
        assert user is not None
        user_id = user.id

    # Create expired share directly via service
    data = AsymmetricShareCreate(
        recipient_id=recipient["id"],
        encrypted_data="enc",
        encrypted_key="key",
        expires_in_hours=-1  # Expired 1 hour ago
    )
    
    with pytest.raises(Exception):
        # The service will throw NotFoundError because it's expired
        share = service.create_share(user_id=user_id, data=data)
        service.get_share_secure(share.id)
