import os
import shutil

# Force file-based SQLite database for backup/restore testing
os.environ["SALUS_TEST_DATABASE_URL"] = "sqlite:///test_salus.db"

import pytest
from sqlmodel import Session, select
from salus.models.user import User as UserModel
from salus.config import settings

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
        # 2. Test GET backups page
        response = authenticated_client.get("/settings/backups")
        assert response.status_code == 200
        assert "Backup &amp; Recovery Control Panel" in response.text
        assert "Enabled &amp; Encrypted" in response.text

        # 3. Test POST create backup
        create_response = authenticated_client.post("/settings/backups/create")
        assert create_response.status_code == 200
        assert "salus_backup_" in create_response.text

        # List backups to extract the newly created file
        from salus.dependencies import get_backup_provider
        provider = get_backup_provider()
        backups = provider.list_backups()
        assert len(backups) > 0
        filename = backups[0]

        # 4. Test POST restore backup
        restore_response = authenticated_client.post(f"/settings/backups/restore/{filename}")
        assert restore_response.status_code == 200
        assert "successfully restored" in restore_response.text

        # 5. Test DELETE backup
        delete_response = authenticated_client.delete(f"/settings/backups/{filename}")
        assert delete_response.status_code == 200
        
        # Confirm it was deleted
        assert filename not in provider.list_backups()

    finally:
        # Restore configuration and clean up files
        settings.backup_password = old_password
        settings.backup_local_dir = old_backup_dir
        if os.path.exists("data/test_backups"):
            shutil.rmtree("data/test_backups")
        if os.path.exists("test_salus.db"):
            try:
                os.remove("test_salus.db")
            except Exception:
                pass
