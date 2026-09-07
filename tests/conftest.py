from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

FileTree = dict[str, "FileTree | str | bytes | None"]


@pytest.fixture
def create_files() -> Callable[[Path, FileTree], None]:
    def _create(root: Path, structure: FileTree) -> None:
        for key, value in structure.items():
            new_path = root / key

            if value is None:
                new_path.touch()
            elif isinstance(value, str):
                new_path.write_text(value)
            elif isinstance(value, bytes):
                new_path.write_bytes(value)
            elif isinstance(value, dict):
                new_path.mkdir(parents=True, exist_ok=True)

                _create(new_path, value)

    return _create


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_creds():
    return MagicMock()


@pytest.fixture
def docx_file(tmp_path, create_files):
    create_files(tmp_path, {"doc.docx": None})
    return tmp_path / "doc.docx"


@pytest.fixture
def mock_get_credentials(monkeypatch):
    mock = MagicMock(return_value=MagicMock())
    monkeypatch.setattr("goodoc.auth.Auth.get_credentials", mock)
    return mock


@pytest.fixture
def mock_upload(monkeypatch):
    mock = MagicMock(return_value="https://docs.google.com/doc")
    monkeypatch.setattr("goodoc.drive.Drive.upload", mock)
    return mock


@pytest.fixture
def mock_browser(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("goodoc.app.webbrowser.open", mock)
    return mock


@pytest.fixture
def mock_drive_build(monkeypatch):
    mock_service = MagicMock()
    mock_service.files.return_value.create.return_value.execute.return_value = {
        "webViewLink": "https://docs.google.com/doc"
    }
    monkeypatch.setattr("goodoc.drive.build", lambda *args, **kwargs: mock_service)
    return mock_service
