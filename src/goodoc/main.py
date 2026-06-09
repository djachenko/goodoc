#!/usr/bin/env python3
"""
goodoc — uploads office files to Google Drive with conversion, opens in browser.

Supported formats:
    .docx  → Google Docs
    .xlsx  → Google Sheets
    .pptx  → Google Slides

Credentials: ~/.goodoc/credentials.json
Token: ~/.goodoc/token.json

Usage:
    goodoc file.docx
    goodoc file.xlsx --no-open
    goodoc setup
"""

import plistlib
import shutil
import uuid
import webbrowser
from pathlib import Path

import typer
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

GOODOC_DIR = Path.home() / ".goodoc"
CREDENTIALS_PATH = GOODOC_DIR / "credentials.json"
TOKEN_PATH = GOODOC_DIR / "token.json"

WORKFLOW_PATH = Path.home() / "Library" / "Services" / "Open in Google Docs.workflow"

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


def _acquire_credentials_file() -> None:
    typer.echo("Step 1: Google Cloud credentials")
    typer.echo()
    typer.echo("  1. Open Google Cloud Console → APIs & Services → Credentials")
    typer.echo("  2. Create a project (or select existing)")
    typer.echo("  3. Enable the Google Drive API:")
    typer.echo("       APIs & Services → Library → search 'Google Drive API' → Enable")
    typer.echo("  4. Create OAuth credentials:")
    typer.echo("       Credentials → + Create Credentials → OAuth client ID")
    typer.echo("       Application type: Desktop app")
    typer.echo("  5. Download the JSON file")
    typer.echo()
    typer.echo("Opening Google Cloud Console in browser...")
    webbrowser.open("https://console.cloud.google.com/apis/credentials")
    typer.echo()

    downloads = Path.home() / "Downloads"
    suggestions = sorted(downloads.glob("client_secret_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    hint = f" [{suggestions[0]}]" if suggestions else ""

    raw = typer.prompt(f"Path to downloaded credentials JSON{hint}").strip()

    if raw:
        src = Path(raw).expanduser()
    elif suggestions:
        src = suggestions[0]
    else:
        typer.echo("No path provided.", err=True)
        raise typer.Exit(1)

    if not src.exists():
        typer.echo(f"File not found: {src}", err=True)
        raise typer.Exit(1)

    GOODOC_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, CREDENTIALS_PATH)
    typer.echo(f"Credentials saved to {CREDENTIALS_PATH}")


def _run_oauth_flow() -> None:
    typer.echo()
    typer.echo("Step 2: Authorize goodoc with Google")
    typer.echo("A browser window will open — sign in and allow access.")
    typer.echo()

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
    creds = flow.run_local_server(port=0)

    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with TOKEN_PATH.open("w") as f:
        f.write(creds.to_json())

    typer.echo(f"Token saved to {TOKEN_PATH}")


def _build_workflow_plist(goodoc_bin: str) -> dict:
    action_uuid = str(uuid.uuid4()).upper()
    input_uuid = str(uuid.uuid4()).upper()
    output_uuid = str(uuid.uuid4()).upper()

    script = f'for f in "$@"; do\n    {goodoc_bin} "$f"\ndone'

    return {
        "AMApplicationBuild": "521.1",
        "AMApplicationVersion": "2.10",
        "AMDocumentVersion": "2",
        "actions": [
            {
                "action": {
                    "AMAccepts": {
                        "Container": "List",
                        "Optional": True,
                        "Types": ["com.apple.cocoa.path"],
                    },
                    "AMActionVersion": "2.0.3",
                    "AMApplication": ["Finder"],
                    "AMParameterProperties": {
                        "COMMAND_STRING": {},
                        "CheckedForUserDefaultShell": {},
                        "inputMethod": {},
                        "shell": {},
                        "source": {},
                    },
                    "AMProvides": {
                        "Container": "List",
                        "Types": ["com.apple.cocoa.path"],
                    },
                    "ActionBundlePath": "/System/Library/Automator/Run Shell Script.action",
                    "ActionName": "Run Shell Script",
                    "ActionParameters": {
                        "COMMAND_STRING": script,
                        "CheckedForUserDefaultShell": True,
                        "inputMethod": 1,
                        "shell": "/bin/zsh",
                        "source": "",
                    },
                    "BundleIdentifier": "com.apple.RunShellScript",
                    "CFBundleVersion": "2.0.3",
                    "CanShowSelectedItemsWhenRun": False,
                    "CanShowWhenRun": True,
                    "Category": ["AMCategoryUtilities"],
                    "Class Name": "RunShellScriptAction",
                    "InputUUID": input_uuid,
                    "Keywords": ["Shell", "Script", "Command", "Run", "Unix"],
                    "OutputUUID": output_uuid,
                    "UUID": action_uuid,
                    "UnlocalizedApplications": ["Finder"],
                    "arguments": {
                        "0": {
                            "default value": 0,
                            "name": "inputMethod",
                            "required": "0",
                            "type": "0",
                            "uuid": "0",
                        },
                        "1": {
                            "default value": "",
                            "name": "source",
                            "required": "0",
                            "type": "0",
                            "uuid": "1",
                        },
                        "2": {
                            "default value": "",
                            "name": "COMMAND_STRING",
                            "required": "0",
                            "type": "0",
                            "uuid": "2",
                        },
                        "3": {
                            "default value": "/bin/sh",
                            "name": "shell",
                            "required": "0",
                            "type": "0",
                            "uuid": "3",
                        },
                    },
                    "isViewVisible": True,
                    "location": "309.5:253.0",
                    "nibPath": "/System/Library/Automator/Run Shell Script.action/Contents/Resources/English.lproj/main.nib",
                },
                "isViewVisible": True,
            }
        ],
        "connectors": {},
        "workflowMetaData": {
            "workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
        },
    }


def _build_info_plist() -> dict:
    return {
        "NSServices": [
            {
                "NSMenuItem": {"default": "Open in Google Docs"},
                "NSMessage": "runWorkflowAsService",
                "NSRequiredContext": {
                    "NSApplicationIdentifier": "com.apple.finder",
                },
                "NSSendFileTypes": ["public.data"],
            }
        ]
    }


def _install_quick_action() -> None:
    typer.echo()
    typer.echo("Step 3: Finder Quick Action")

    goodoc_bin = shutil.which("goodoc") or "goodoc"

    contents = WORKFLOW_PATH / "Contents"
    contents.mkdir(parents=True, exist_ok=True)

    with (contents / "document.wflow").open("wb") as f:
        plistlib.dump(_build_workflow_plist(goodoc_bin), f, fmt=plistlib.FMT_XML)

    with (contents / "Info.plist").open("wb") as f:
        plistlib.dump(_build_info_plist(), f, fmt=plistlib.FMT_XML)

    typer.echo(f"Workflow installed: {WORKFLOW_PATH}")
    typer.echo()
    typer.echo("To enable the Quick Action in Finder right-click menu:")
    typer.echo("  System Settings → Privacy & Security → Extensions → Finder Extensions")
    typer.echo("  — check 'Open in Google Docs'")
    typer.echo()
    typer.echo("Opening System Settings...")
    webbrowser.open("x-apple.systempreferences:com.apple.ExtensionsPreferences")


@app.command()
def setup() -> None:
    """Set up goodoc: OAuth credentials and Finder Quick Action."""
    if not CREDENTIALS_PATH.exists():
        _acquire_credentials_file()
    else:
        typer.echo(f"Credentials already present: {CREDENTIALS_PATH}")

    if not TOKEN_PATH.exists():
        _run_oauth_flow()
    else:
        typer.echo(f"Token already present: {TOKEN_PATH}")

    _install_quick_action()

    typer.echo()
    typer.echo("Setup complete. Run 'goodoc file.docx' to upload a file.")


@app.command()
def main(
    file: Path = typer.Argument(..., help="Path to file (.docx / .xlsx / .pptx)"),
    no_open: bool = typer.Option(False, "--no-open", help="Do not open in browser"),
) -> None:
    """Upload an office file to Google Drive and open it in the browser."""
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
