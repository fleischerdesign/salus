import logging
import os
import xml.etree.ElementTree as ET
from typing import Optional, Protocol, runtime_checkable
from urllib.parse import unquote
import httpx


@runtime_checkable
class IBackupStorageProvider(Protocol):
    def upload_backup(self, filename: str, content: bytes) -> None:
        """Uploads the backup payload to the destination storage."""
        ...

    def download_backup(self, filename: str) -> bytes:
        """Downloads the backup payload from the destination storage."""
        ...

    def list_backups(self) -> list[str]:
        """Lists filenames of backups currently in the storage."""
        ...

    def delete_backup(self, filename: str) -> None:
        """Deletes a backup file from the storage."""
        ...


class LocalBackupProvider:
    def __init__(self, directory: str) -> None:
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def upload_backup(self, filename: str, content: bytes) -> None:
        filepath = os.path.join(self.directory, filename)
        with open(filepath, "wb") as f:
            f.write(content)

    def download_backup(self, filename: str) -> bytes:
        filepath = os.path.join(self.directory, filename)
        with open(filepath, "rb") as f:
            return f.read()

    def list_backups(self) -> list[str]:
        if not os.path.exists(self.directory):
            return []
        return [
            f
            for f in os.listdir(self.directory)
            if os.path.isfile(os.path.join(self.directory, f))
        ]

    def delete_backup(self, filename: str) -> None:
        filepath = os.path.join(self.directory, filename)
        if os.path.exists(filepath):
            os.remove(filepath)


class WebdavBackupProvider:
    def __init__(
        self,
        url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        self.url = url.rstrip("/")
        self.auth = (username, password) if username and password else None

    def upload_backup(self, filename: str, content: bytes) -> None:
        target_url = f"{self.url}/{filename}"
        with httpx.Client(auth=self.auth) as client:
            resp = client.put(target_url, content=content)
            resp.raise_for_status()

    def download_backup(self, filename: str) -> bytes:
        target_url = f"{self.url}/{filename}"
        with httpx.Client(auth=self.auth) as client:
            resp = client.get(target_url)
            resp.raise_for_status()
            return resp.content

    def list_backups(self) -> list[str]:
        headers = {"Depth": "1"}
        with httpx.Client(auth=self.auth) as client:
            try:
                resp = client.request("PROPFIND", self.url, headers=headers)
                if resp.status_code >= 400:
                    return []

                root = ET.fromstring(resp.content)
                filenames = []
                ns = {"d": "DAV:"}
                for response in root.findall(".//d:response", ns):
                    href = response.find("d:href", ns)
                    if href is not None and href.text:
                        path = unquote(href.text)
                        fname = path.split("/")[-1]
                        if fname:
                            filenames.append(fname)
                return filenames
            except Exception:
                logging.getLogger(__name__).warning("Failed to list WebDAV backups", exc_info=True)
                return []

    def delete_backup(self, filename: str) -> None:
        target_url = f"{self.url}/{filename}"
        with httpx.Client(auth=self.auth) as client:
            resp = client.delete(target_url)
            resp.raise_for_status()
