import os
import webbrowser
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

import typer

from goodoc.auth import get_credentials
from goodoc.drive import upload

app = typer.Typer(add_completion=False)


@dataclass(frozen=True)
class Config:
    goodoc_dir: Path = field(default_factory=lambda: Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "goodoc")
    scopes: list[str] = field(default_factory=lambda: ["https://www.googleapis.com/auth/drive.file"])

    @cached_property
    def credentials_path(self) -> Path:
        return self.goodoc_dir / "credentials.json"

    @cached_property
    def token_path(self) -> Path:
        return self.goodoc_dir / "token.json"


@app.command()
def main(
    files: list[Path] = typer.Argument(..., help="Paths to files (.docx / .xlsx / .pptx / .pptm)"),
    no_open: bool = typer.Option(False, "--no-open", help="Do not open in browser"),
) -> None:
    """Upload office files to Google Drive and open them in the browser."""
    config = Config()
    creds = get_credentials(config)

    for file in files:
        if not file.exists():
            typer.echo(f"File not found: {file}", err=True)

            raise typer.Exit(1)

        typer.echo(f"Uploading {file.name}...")
        url = upload(file, creds)
        typer.echo(url)

        if not no_open:
            webbrowser.open(url)


if __name__ == "__main__":
    app()
