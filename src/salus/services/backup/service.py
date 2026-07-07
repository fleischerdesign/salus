import os
import re
import subprocess
from datetime import datetime
from sqlalchemy import text, Engine
from typing import Optional

from salus.services.backup.crypto import encrypt, decrypt
from salus.services.backup.providers import IBackupStorageProvider


class BackupService:
    def __init__(
        self,
        engine: Engine,
        database_url: str,
        password: Optional[str],
        provider: IBackupStorageProvider,
        retention_days: int = 14,
    ) -> None:
        self.engine = engine
        self.database_url = database_url
        self.password = password
        self.provider = provider
        self.retention_days = retention_days

    def run_backup(self) -> str:
        """
        Executes a database snapshot dump, encrypts it, uploads it,
        and enforces the retention policy.
        Returns: the filename of the uploaded backup.
        """
        if not self.password:
            raise ValueError(
                "Backup service is disabled. Set SALUS_BACKUP_PASSWORD to enable."
            )

        # 1. Capture Database Bytes
        if "postgresql" in self.database_url or "postgres" in self.database_url:
            db_bytes = self._dump_postgres()
        else:
            db_bytes = self._dump_sqlite()

        # 2. Encrypt
        encrypted_payload = encrypt(db_bytes, self.password)

        # 3. Upload
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"salus_backup_{timestamp}.enc"
        self.provider.upload_backup(filename, encrypted_payload)

        # 4. Enforce Retention
        self.enforce_retention()

        return filename

    def restore_backup(self, filename: str, restore_db_path: str) -> None:
        """
        Retrieves a backup, decrypts it, and writes it to restore_db_path.
        Warning: This will overwrite target file contents. Only use SQLite destination.
        """
        if not self.password:
            raise ValueError("Backup password is required for restoration.")

        # Download
        backups = self.provider.list_backups()
        if filename not in backups:
            raise FileNotFoundError(f"Backup file '{filename}' not found in storage.")

        encrypted_payload = self.provider.download_backup(filename)
        decrypted_payload = decrypt(encrypted_payload, self.password)

        with open(restore_db_path, "wb") as f:
            f.write(decrypted_payload)

    def enforce_retention(self) -> int:
        """
        Removes backups older than retention_days.
        Returns the number of deleted backups.
        """
        backups = self.provider.list_backups()
        deleted_count = 0
        now = datetime.now()

        for fname in backups:
            # Match salus_backup_YYYY-MM-DD_HH-MM-SS.enc
            match = re.match(
                r"salus_backup_(\d{4}-\d{2}-\d{2})_(\d{2}-\d{2}-\d{2})\.enc", fname
            )
            if match:
                dt_str = f"{match.group(1)} {match.group(2).replace('-', ':')}"
                try:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                    if (now - dt).days > self.retention_days:
                        self.provider.delete_backup(fname)
                        deleted_count += 1
                except Exception:
                    pass
        return deleted_count

    def _dump_sqlite(self) -> bytes:
        # SQLite Vacuum Into snapshot
        temp_path = os.path.join(os.getcwd(), "temp_vacuum_backup.db")
        if os.path.exists(temp_path):
            os.remove(temp_path)

        try:
            with self.engine.begin() as conn:
                conn.execute(text(f"VACUUM INTO '{temp_path}'"))
            with open(temp_path, "rb") as f:
                db_bytes = f.read()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return db_bytes

    def _dump_postgres(self) -> bytes:
        cmd = ["pg_dump", "--clean", "--no-owner", "--no-acl", self.database_url]
        res = subprocess.run(cmd, capture_output=True)
        if res.returncode != 0:
            raise RuntimeError(f"pg_dump failed: {res.stderr.decode()}")
        return res.stdout
