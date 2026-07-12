import os
import shutil
from sqlmodel import Session, select
from salus.models.user import User as UserModel
from salus.config import settings


def test_backup_ui_endpoints(authenticated_client):
    old_backup_dir = settings.backup_local_dir
    settings.backup_local_dir = "data/test_backups"
    if os.path.exists("data/test_backups"):
        shutil.rmtree("data/test_backups")
    os.makedirs("data/test_backups", exist_ok=True)

    engine = authenticated_client.app.state.engine
    with Session(engine) as session:
        alice = session.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None
        alice.is_admin = True
        session.add(alice)
        session.commit()

    old_password = settings.backup_password
    settings.backup_password = "test-crypt-secret"

    try:
        response = authenticated_client.get("/api/v1/admin/backups")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

        create_response = authenticated_client.post("/api/v1/admin/backups")
        assert create_response.status_code == 201
        data = create_response.json()
        assert "salus_backup_" in data["filename"]

        from salus.dependencies import get_backup_provider

        provider = get_backup_provider()
        backups = provider.list_backups()
        assert len(backups) > 0
        filename = backups[0]

        dummy_content = b"encrypted-payload-bytes"
        upload_filename = "salus_backup_2026-07-09_12-00-00.enc"
        upload_response = authenticated_client.post(
            "/api/v1/admin/backups/upload",
            files={"backup_file": (upload_filename, dummy_content, "application/octet-stream")},
        )
        assert upload_response.status_code == 200
        assert upload_filename in provider.list_backups()

        restore_response = authenticated_client.post(f"/api/v1/admin/backups/{filename}/restore")
        assert restore_response.status_code == 200

        delete_response = authenticated_client.delete(f"/api/v1/admin/backups/{filename}")
        assert delete_response.status_code == 204
        assert filename not in provider.list_backups()

        provider.delete_backup(upload_filename)

    finally:
        settings.backup_password = old_password
        settings.backup_local_dir = old_backup_dir
        if os.path.exists("data/test_backups"):
            shutil.rmtree("data/test_backups")
