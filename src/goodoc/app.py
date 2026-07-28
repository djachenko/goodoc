import webbrowser
from pathlib import Path

import typer

from goodoc.auth import Auth
from goodoc.config import Config
from goodoc.drive import MIME_MAP, Drive


class App:
    def __init__(self, config: Config, auth: Auth, drive: Drive) -> None:
        self._config = config
        self._auth = auth
        self._drive = drive

    def upload(self, files: list[Path], open_browser: bool) -> None:
        for file in files:
            if error_message := self.validate(file):
                typer.echo(error_message, err=True)

                raise typer.Exit(1)

        for file in files:
            typer.echo(f"Uploading {file.name}...")

            url = self._drive.upload(file)
            typer.echo(url)

            if open_browser:
                webbrowser.open(url)

    def login(self, key: str | None = None) -> None:
        if key is None:
            self._auth.get_credentials()
        else:
            try:
                self._auth.login_shared(key)
            except ValueError as error:
                typer.echo(str(error), err=True)

                raise typer.Exit(1)

        typer.echo("Logged in.")

    def logout(self) -> None:
        if self._config.token_path.exists():
            self._config.token_path.unlink()

            typer.echo("Logged out.")
        else:
            typer.echo("Not logged in.")

    @staticmethod
    def validate(file: Path) -> str | None:
        if not file.exists():
            return f"File not found: {file}"

        if file.suffix.lower() not in MIME_MAP:
            supported = ", ".join(MIME_MAP)

            return f"Unsupported format: {file.suffix}. Supported: {supported}"

        return None
