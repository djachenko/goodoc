import shutil
import sys
import webbrowser
from pathlib import Path

import typer
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from goodoc.client import client_config
from goodoc.config import Config


class Setup:
    def __init__(self, config: Config) -> None:
        self._config = config

    def authorize_shared(self, access_key: str) -> Credentials:
        flow = InstalledAppFlow.from_client_config(client_config(access_key), self._config.scopes)

        return flow.run_local_server(port=0)

    def first_run_wizard(self) -> Credentials:
        if not sys.stdin.isatty():
            typer.echo("goodoc is not configured. Run 'goodoc <file>' from Terminal first.", err=True)

            raise typer.Exit(1)

        typer.echo("First run — goodoc needs a Google Cloud project of its own.")
        typer.echo("Takes a few minutes, once.")
        typer.echo()
        typer.echo("Got an access key from the author? Cancel and run instead:")
        typer.echo("  goodoc login --key <KEY>")
        typer.echo()

        self._acquire_credentials()

        typer.echo()
        typer.echo("A browser window will open — sign in and allow access.")
        typer.echo()

        flow = InstalledAppFlow.from_client_secrets_file(str(self._config.credentials_path), self._config.scopes)

        return flow.run_local_server(port=0)

    def _acquire_credentials(self) -> None:
        typer.echo("Set up your own Google Cloud project:")
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

        self._config.goodoc_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, self._config.credentials_path)

        typer.echo(f"Saved to {self._config.credentials_path}")
