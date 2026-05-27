#!/usr/bin/env python3
"""
goodoc — uploads office files to Google Drive with conversion, opens in browser.

Supported formats:
    .docx  → Google Docs
    .xlsx  → Google Sheets
    .pptx  → Google Slides
    .pptm  → Google Slides

Credentials: ~/.goodoc/credentials.json
Token: ~/.goodoc/token.json

Usage:
    goodoc file.docx
    goodoc file.xlsx --no-open
"""

from pathlib import Path

import typer
import webbrowser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

GOODOC_DIR = Path.home() / ".goodoc"
CREDENTIALS_PATH = GOODOC_DIR / "credentials.json"
TOKEN_PATH = GOODOC_DIR / "token.json"

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
    ".pptm": (
        "application/vnd.ms-powerpoint.presentation.macroEnabled.12",
        "application/vnd.google-apps.presentation",
    ),
}

app = typer.Typer(add_completion=False)


def get_credentials() -> Credentials:
    if not CREDENTIALS_PATH.exists():
        typer.echo(f"credentials.json not found: {CREDENTIALS_PATH}", err=True)
        typer.echo("Place your OAuth credentials from Google Cloud Console at ~/.goodoc/credentials.json", err=True)

        raise typer.Exit(1)

    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        with TOKEN_PATH.open("w") as f:
            f.write(creds.to_json())

    return creds


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


@app.command()
def main(
    file: Path = typer.Argument(..., help="Path to file (.docx / .xlsx / .pptx)"),
    no_open: bool = typer.Option(False, "--no-open", help="Do not open in browser"),
) -> None:
    if not file.exists():
        typer.echo(f"File not found: {file}", err=True)

        raise typer.Exit(1)

    typer.echo(f"Uploading {file.name}...")

    creds = get_credentials()
    url = upload(file, creds)

    typer.echo(url)

    if not no_open:
        webbrowser.open(url)


if __name__ == "__main__":
    app()
