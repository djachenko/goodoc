import webbrowser
from pathlib import Path
from typing import Any

import typer
from typer.core import TyperGroup

from goodoc.auth import Auth
from goodoc.config import Config
from goodoc.drive import MIME_MAP, upload

DEFAULT_COMMAND = "upload"


class DefaultCommandGroup(TyperGroup):
    def parse_args(self, ctx: Any, args: list[str]) -> list[str]:
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            args = [DEFAULT_COMMAND, *args]

        return super().parse_args(ctx, args)


app = typer.Typer(cls=DefaultCommandGroup, no_args_is_help=True)


def validate_file(file: Path) -> str | None:
    if not file.exists():
        return f"File not found: {file}"

    if file.suffix.lower() not in MIME_MAP:
        supported = ", ".join(MIME_MAP)
        return f"Unsupported format: {file.suffix}. Supported: {supported}"

    return None


@app.command(DEFAULT_COMMAND)
def upload_files(
        files: list[Path] = typer.Argument(..., help=f"Paths to files ({' / '.join(MIME_MAP)})"),
        no_open: bool = typer.Option(False, "--no-open", help="Do not open in browser"),
) -> None:
    """Upload office files to Google Drive and open them in the browser."""
    config = Config.default()

    for file in files:
        if error := validate_file(file):
            typer.echo(error, err=True)

            raise typer.Exit(1)

    creds = Auth.get_credentials(config)

    for file in files:
        typer.echo(f"Uploading {file.name}...")

        url = upload(file, creds)
        typer.echo(url)

        if not no_open:
            webbrowser.open(url)


@app.command()
def login(
        key: str | None = typer.Option(None, "--key", help="Access key for the author's shared client"),
) -> None:
    """Authenticate with Google (without uploading a file)."""
    config = Config.default()

    if key is None:
        Auth.get_credentials(config)
    else:
        try:
            Auth.login_shared(config, key)
        except ValueError as error:
            typer.echo(str(error), err=True)

            raise typer.Exit(1)

    typer.echo("Logged in.")


@app.command()
def logout() -> None:
    """Remove stored token (re-authentication will be required on next run)."""
    config = Config.default()

    if config.token_path.exists():
        config.token_path.unlink()
        typer.echo("Logged out.")
    else:
        typer.echo("Not logged in.")


if __name__ == "__main__":
    app()
