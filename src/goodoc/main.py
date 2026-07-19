import webbrowser
from pathlib import Path

import typer

from goodoc.auth import get_credentials
from goodoc.config import Config
from goodoc.drive import MIME_MAP, upload

app = typer.Typer()


def validate_file(file: Path) -> str | None:
    if not file.exists():
        return f"File not found: {file}"

    if file.suffix.lower() not in MIME_MAP:
        supported = ", ".join(MIME_MAP)
        return f"Unsupported format: {file.suffix}. Supported: {supported}"

    return None


@app.command()
def main(
        files: list[Path] = typer.Argument(..., help="Paths to files (.docx / .xlsx / .pptx / .pptm)"),
        no_open: bool = typer.Option(False, "--no-open", help="Do not open in browser"),
) -> None:
    """Upload office files to Google Drive and open them in the browser."""
    config = Config.default()

    for file in files:
        if error := validate_file(file):
            typer.echo(error, err=True)

            raise typer.Exit(1)

    creds = get_credentials(config)

    for file in files:
        typer.echo(f"Uploading {file.name}...")
        url = upload(file, creds)
        typer.echo(url)

        if not no_open:
            webbrowser.open(url)


if __name__ == "__main__":
    app()
