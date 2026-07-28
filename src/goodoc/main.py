from pathlib import Path
from typing import Any

import typer
from typer.core import TyperGroup

from goodoc.app import App
from goodoc.auth import Auth
from goodoc.config import Config
from goodoc.drive import MIME_MAP, Drive
from goodoc.setup import Setup

DEFAULT_COMMAND = "upload"


class DefaultCommandGroup(TyperGroup):
    def parse_args(self, ctx: Any, args: list[str]) -> list[str]:
        if args and args[0] not in self.commands and not args[0].startswith("-"):
            args = [DEFAULT_COMMAND, *args]

        return super().parse_args(ctx, args)


def _create_app() -> App:
    config = Config.default()
    setup = Setup(config)
    auth = Auth(config, setup)
    drive = Drive(auth)
    local_app = App(config, auth, drive)

    return local_app


app = typer.Typer(cls=DefaultCommandGroup, no_args_is_help=True)
_app = _create_app()


@app.command(DEFAULT_COMMAND)
def upload(
        files: list[Path] = typer.Argument(..., help=f"Paths to files ({' / '.join(MIME_MAP)})"),  # noqa: B008
        no_open: bool = typer.Option(False, "--no-open", help="Do not open in browser"),
) -> None:
    """Upload office files to Google Drive and open them in the browser."""
    _app.upload(files, open_browser=not no_open)


@app.command()
def login(
        key: str | None = typer.Option(None, "--key", help="Access key for the author's shared client"),
) -> None:
    """Authenticate with Google (without uploading a file)."""
    _app.login(key)


@app.command()
def logout() -> None:
    """Remove stored token (re-authentication will be required on next run)."""
    _app.logout()


if __name__ == "__main__":
    app()
