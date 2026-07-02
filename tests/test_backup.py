import os
import time
import pytest
from datetime import datetime, timedelta
from cryptography.exceptions import InvalidTag
from sqlmodel import SQLModel, create_engine, select

from salus.config import settings
from salus.services.backup.crypto import encrypt, decrypt
from salus.services.backup.providers import LocalBackupProvider
from salus.services.backup.service import BackupService


def test_crypto_encryption_decryption():
    password = "super-secret-backup-pass"
    plaintext = b"Hello, Salus DB data!"

    # Encrypt
    ciphertext = encrypt(plaintext, password)
    assert ciphertext != plaintext
    assert len(ciphertext) > len(plaintext)

    # Decrypt
    decrypted = decrypt(ciphertext, password)
    assert decrypted == plaintext


def test_crypto_decryption_with_wrong_password():
    password = "correct-pass"
    wrong_password = "wrong-pass"
    plaintext = b"Secret text"

    ciphertext = encrypt(plaintext, password)
    with pytest.raises(Exception):  # Cryptography raises InvalidTag for GCM verification failure
        decrypt(ciphertext, wrong_password)


def test_crypto_tampering_detection():
    password = "pass"
    plaintext = b"Sensitive information"
    ciphertext = encrypt(plaintext, password)

    # Tamper with a single byte in ciphertext
    tampered = bytearray(ciphertext)
    tampered[-5] ^= 0x01  # flip a bit

    with pytest.raises(InvalidTag):
        decrypt(bytes(tampered), password)


def test_local_backup_provider(tmp_path):
    provider = LocalBackupProvider(str(tmp_path))
    filename = "test_file.enc"
    payload = b"some-encrypted-bytes"

    # Upload
    provider.upload_backup(filename, payload)
    assert os.path.exists(tmp_path / filename)

    # List
    files = provider.list_backups()
    assert filename in files

    # Download
    content = provider.download_backup(filename)
    assert content == payload

    # Delete
    provider.delete_backup(filename)
    assert not os.path.exists(tmp_path / filename)
    assert filename not in provider.list_backups()


def test_backup_service_sqlite_dump_and_retention(tmp_path):
    # Setup test DB engine
    test_db_file = tmp_path / "test_salus.db"
    db_url = f"sqlite:///{test_db_file}"
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)

    # Insert some dummy table data
    # (Just verifying it can create hot copy of tables successfully)
    from sqlalchemy import text
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE dummy (id INTEGER PRIMARY KEY, val TEXT)"))
        conn.execute(text("INSERT INTO dummy (val) VALUES ('test-data')"))

    # Setup local backup destination
    backup_dir = tmp_path / "backups"
    provider = LocalBackupProvider(str(backup_dir))

    # Instantiate BackupService
    service = BackupService(
        engine=engine,
        database_url=db_url,
        password="backup-password-123",
        provider=provider,
        retention_days=1,  # 1 day retention
    )

    # Run backup
    filename = service.run_backup()
    assert filename.startswith("salus_backup_")
    assert filename.endswith(".enc")

    # Verify backup file exists and is encrypted (cannot be read directly as SQLite db)
    backup_filepath = backup_dir / filename
    assert os.path.exists(backup_filepath)
    with open(backup_filepath, "rb") as f:
        header = f.read(100)
    assert b"SQLite format 3" not in header

    # Restore backup to a new file and verify
    restore_file = tmp_path / "restored.db"
    service.restore_backup(filename, str(restore_file))
    assert os.path.exists(restore_file)

    # Check restored DB contents
    restore_engine = create_engine(f"sqlite:///{restore_file}")
    with restore_engine.connect() as conn:
        res = conn.execute(text("SELECT val FROM dummy")).first()
        assert res is not None
        assert res[0] == "test-data"


def test_backup_service_retention_purge(tmp_path):
    backup_dir = tmp_path / "backups"
    provider = LocalBackupProvider(str(backup_dir))

    # Add mock files with timestamped names
    # 1. 5 days old (should be purged if retention=2)
    provider.upload_backup("salus_backup_2026-06-25_12-00-00.enc", b"old-data")
    # 2. Today (should be kept)
    today_str = datetime.now().strftime("%Y-%m-%d")
    provider.upload_backup(f"salus_backup_{today_str}_12-00-00.enc", b"new-data")

    # Setup BackupService
    dummy_engine = create_engine("sqlite://")
    service = BackupService(
        engine=dummy_engine,
        database_url="sqlite://",
        password="pass",
        provider=provider,
        retention_days=2,
    )

    deleted_count = service.enforce_retention()
    assert deleted_count == 1

    remaining = provider.list_backups()
    assert len(remaining) == 1
    assert remaining[0].startswith(f"salus_backup_{today_str}")
