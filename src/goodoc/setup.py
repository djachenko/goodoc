from __future__ import annotations

import shutil
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING

import typer
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

if TYPE_CHECKING:
    from goodoc.main import Config


def acquire_credentials(config: Config) -> None:
    typer.echo("Step 1/2: Google Cloud credentials")
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
    typer.echo("Step 2/2: Authorize goodoc with Google")
    typer.echo("A browser window will open — sign in and allow access.")
    typer.echo()

    flow = InstalledAppFlow.from_client_secrets_file(str(config.credentials_path), config.scopes)
    creds = flow.run_local_server(port=0)

    config.token_path.parent.mkdir(parents=True, exist_ok=True)
    with config.token_path.open("w") as f:
        f.write(creds.to_json())

    typer.echo(f"Token saved to {config.token_path}")

    return creds


def first_run_wizard(config: Config) -> Credentials:
    typer.echo("First run — let's set up goodoc.")
    typer.echo()

    acquire_credentials(config)
    creds = authorize(config)

    typer.echo()
    typer.echo("All done. Run 'goodoc <file>' to upload.")
    typer.echo()

    return creds
