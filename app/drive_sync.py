from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from google.oauth2 import service_account
from googleapiclient.discovery import build


@dataclass
class DriveFile:
    file_id: str
    name: str
    mime_type: str
    modified_time: str
    web_view_link: str | None
    local_path: str | None = None


class LocalFolderDriveClient:
    def __init__(self, folder: str):
        self.folder = Path(folder)

    def list_files(self) -> Iterable[DriveFile]:
        for p in self.folder.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".pdf", ".docx", ".doc", ".txt"}:
                stat = p.stat()
                yield DriveFile(
                    file_id=str(p.relative_to(self.folder)),
                    name=p.name,
                    mime_type="local/file",
                    modified_time=str(stat.st_mtime),
                    web_view_link=None,
                    local_path=str(p),
                )


class GoogleDriveClient:
    def __init__(self, service_account_file: str):
        creds = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
        self.service = build("drive", "v3", credentials=creds, cache_discovery=False)

    def list_files(self, folder_id: str):
        page_token = None
        query = f"'{folder_id}' in parents and trashed = false"
        while True:
            resp = self.service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType, modifiedTime, webViewLink)",
                pageToken=page_token,
                includeItemsFromAllDrives=True,
                supportsAllDrives=True,
            ).execute()
            for f in resp.get("files", []):
                yield DriveFile(
                    file_id=f["id"],
                    name=f["name"],
                    mime_type=f["mimeType"],
                    modified_time=f["modifiedTime"],
                    web_view_link=f.get("webViewLink"),
                )
            page_token = resp.get("nextPageToken")
            if not page_token:
                break
