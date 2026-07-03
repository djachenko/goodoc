from pathlib import Path

import typer
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

MIME_MAP = {
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.google-apps.document",
    ),
    ".xlsx": (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.google-apps.spreadsheet",
    ),
    ".pptx": (
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "application/vnd.google-apps.presentation",
    ),
}


def upload(path: Path, creds: Credentials) -> str:
    suffix = path.suffix.lower()

    if suffix not in MIME_MAP:
        supported = ", ".join(MIME_MAP)
        typer.echo(f"Unsupported format: {suffix}. Supported: {supported}", err=True)

        raise typer.Exit(1)

    source_mime, target_mime = MIME_MAP[suffix]

    service = build("drive", "v3", credentials=creds)
    media = MediaFileUpload(str(path), mimetype=source_mime, resumable=False)

    result = (
        service.files()
        .create(
            body={"name": path.stem, "mimeType": target_mime},
            media_body=media,
            fields="id,webViewLink",
        )
        .execute()
    )

    return result["webViewLink"]
