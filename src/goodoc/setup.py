from __future__ import annotations

import plistlib
import shutil
import uuid
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

if TYPE_CHECKING:
    from goodoc.main import Config


def acquire_credentials(config: Config) -> None:
    typer.echo("Step 1/3: Google Cloud credentials")
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

    config.goodoc_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, config.credentials_path)
    typer.echo(f"Saved to {config.credentials_path}")


def authorize(config: Config) -> Credentials:
    typer.echo()
    typer.echo("Step 2/3: Authorize goodoc with Google")
    typer.echo("A browser window will open — sign in and allow access.")
    typer.echo()

    flow = InstalledAppFlow.from_client_secrets_file(str(config.credentials_path), config.scopes)
    creds = flow.run_local_server(port=0)

    config.token_path.parent.mkdir(parents=True, exist_ok=True)
    with config.token_path.open("w") as f:
        f.write(creds.to_json())

    typer.echo(f"Token saved to {config.token_path}")

    return creds


def install_quick_action(config: Config) -> None:
    typer.echo()
    typer.echo("Step 3/3: Finder Quick Action")

    goodoc_bin = _find_goodoc_bin()
    contents = config.workflow_path / "Contents"
    contents.mkdir(parents=True, exist_ok=True)

    with (contents / "document.wflow").open("wb") as f:
        plistlib.dump(_build_workflow_plist(goodoc_bin), f, fmt=plistlib.FMT_XML)

    with (contents / "Info.plist").open("wb") as f:
        plistlib.dump(_build_info_plist(), f, fmt=plistlib.FMT_XML)

    typer.echo(f"Installed: {config.workflow_path}")
    typer.echo()
    typer.echo("Enable in: System Settings → Privacy & Security → Extensions → Finder Extensions")
    typer.echo("           check 'Open in Google Docs'")
    typer.echo()
    typer.echo("Opening System Settings...")
    webbrowser.open("x-apple.systempreferences:com.apple.ExtensionsPreferences")


def first_run_wizard(config: Config) -> Credentials:
    typer.echo("First run — let's set up goodoc.")
    typer.echo()

    acquire_credentials(config)
    creds = authorize(config)
    install_quick_action(config)

    typer.echo()
    typer.echo("All done. Continuing...")
    typer.echo()

    return creds


def _find_goodoc_bin() -> str:
    candidates = [
        Path.home() / ".local" / "bin" / "goodoc",  # pipx default
        Path("/usr/local/bin/goodoc"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    found = shutil.which("goodoc")
    if found and ".venv" not in found:
        return found

    return "goodoc"


def _build_workflow_plist(goodoc_bin: str) -> dict:
    action_uuid = str(uuid.uuid4()).upper()
    input_uuid = str(uuid.uuid4()).upper()
    output_uuid = str(uuid.uuid4()).upper()

    script = f'export PATH="$HOME/.local/bin:/usr/local/bin:$PATH"\nfor f in "$@"; do\n    {goodoc_bin} "$f"\ndone'

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
