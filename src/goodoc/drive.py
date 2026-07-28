from pathlib import Path

import typer
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from goodoc.auth import Auth

MIME_MAP = {
    ".doc": (
        "application/msword",
        "application/vnd.google-apps.document",
    ),
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.google-apps.document",
    ),
    ".xls": (
        "application/vnd.ms-excel",
        "application/vnd.google-apps.spreadsheet",
    ),
    ".xlsx": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.google-apps.spreadsheet",
    ),
    ".ppt": (
        "application/vnd.ms-powerpoint",
        "application/vnd.google-apps.presentation",
    ),
    ".pptx": (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.google-apps.presentation",
    ),
    ".pptm": (
        "application/vnd.ms-powerpoint.presentation.macroEnabled.12",
        "application/vnd.google-apps.presentation",
    ),
}


class Drive:
    def __init__(self, auth: Auth) -> None:
        self._auth = auth

    def upload(self, path: Path) -> str:
        suffix = path.suffix.lower()

        if suffix not in MIME_MAP:
            supported = ", ".join(MIME_MAP)
            typer.echo(f"Unsupported format: {suffix}. Supported: {supported}", err=True)

            raise typer.Exit(1)

        source_mime, target_mime = MIME_MAP[suffix]
        creds = self._auth.get_credentials()

        service = build("drive", "v3", credentials=creds)
        media = MediaFileUpload(str(path), mimetype=source_mime, resumable=False)

        result = (
            service.files()
            .create(
                body={
                    "name": path.stem,
                    "mimeType": target_mime,
                },
                media_body=media,
                fields="id,webViewLink",
            )
            .execute()
        )

        return result["webViewLink"]
