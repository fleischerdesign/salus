import os
import shutil
import pytest
from sqlmodel import Session, select
from salus.models.user import User as UserModel
from salus.config import settings

@pytest.fixture
def client():
    # Force file-based SQLite database for this test file only
    db_path = "test_salus.db"
    db_url = f"sqlite:///{db_path}"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

    from sqlalchemy import create_engine
    from sqlmodel import SQLModel, Session
    from salus.database import get_session
    from salus.main import app, templates
    from salus.services.config import ConfigService
    from salus.repositories.system_config import SystemConfigRepository
    from fastapi.testclient import TestClient
    
    engine = create_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False},
    )
    
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    
    from tests.conftest import _seed_admin
    _seed_admin(Session(engine))
    
    def override_get_session():
        return Session(engine)
        
    app.dependency_overrides[get_session] = override_get_session
    app.state.templates = templates
    app.state.engine = engine
    
    session = Session(engine)
    try:
        ConfigService(SystemConfigRepository(session)).seed_defaults()
    finally:
        session.close()
        
    with TestClient(app) as test_client:
        yield test_client
        
    app.dependency_overrides.clear()
    
    # Cleanup database file
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass


def test_backup_ui_endpoints(authenticated_client):
    # Setup test directories
    old_backup_dir = settings.backup_local_dir
    settings.backup_local_dir = "data/test_backups"
    if os.path.exists("data/test_backups"):
        shutil.rmtree("data/test_backups")
    os.makedirs("data/test_backups", exist_ok=True)

    # 1. Make Alice an admin to pass require_admin checks
    engine = authenticated_client.app.state.engine
    with Session(engine) as session:
        alice = session.exec(select(UserModel).where(UserModel.username == "alice")).first()
        assert alice is not None
        alice.is_admin = True
        session.add(alice)
        session.commit()

    # Ensure a backup password is set for tests
    old_password = settings.backup_password
    settings.backup_password = "test-crypt-secret"

    try:
        # 2. Test GET admin general page containing the backups panel
        response = authenticated_client.get("/admin")
        assert response.status_code == 200
        assert "Encrypted Backups (Zero-Knowledge)" in response.text
        assert "Enabled &amp; Encrypted" in response.text

        # 3. Test POST create backup
        create_response = authenticated_client.post("/admin/backups/run")
        assert create_response.status_code == 200
        assert "salus_backup_" in create_response.text

        # List backups to extract the newly created file
        from salus.dependencies import get_backup_provider
        provider = get_backup_provider()
        backups = provider.list_backups()
        assert len(backups) > 0
        filename = backups[0]

        # 4. Test POST upload backup
        dummy_content = b"encrypted-payload-bytes"
        upload_filename = "salus_backup_2026-07-09_12-00-00.enc"
        upload_response = authenticated_client.post(
            "/admin/backups/upload",
            files={"backup_file": (upload_filename, dummy_content, "application/octet-stream")},
        )
        assert upload_response.status_code == 200
        assert upload_filename in upload_response.text
        assert upload_filename in provider.list_backups()

        # 5. Test POST restore backup
        restore_response = authenticated_client.post(f"/admin/backups/restore/{filename}")
        assert restore_response.status_code == 200
        assert "successfully restored" in restore_response.text

        # 6. Test DELETE backup
        delete_response = authenticated_client.delete(f"/admin/backups/{filename}")
        assert delete_response.status_code == 200
        assert filename not in provider.list_backups()

        # Clean up uploaded test file
        provider.delete_backup(upload_filename)

    finally:
        # Restore configuration and clean up files
        settings.backup_password = old_password
        settings.backup_local_dir = old_backup_dir
        if os.path.exists("data/test_backups"):
            shutil.rmtree("data/test_backups")
