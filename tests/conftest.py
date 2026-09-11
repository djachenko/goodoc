from collections.abc import Callable
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner

FileTree = dict[str, "FileTree | str | None"]
CreateFiles = Callable[[Path, FileTree], None]


@pytest.fixture
def create_files() -> CreateFiles:
    def _create(root: Path, structure: FileTree) -> None:
        for key, value in structure.items():
            path = root / key

            if value is None:
                path.touch()
            elif isinstance(value, str):
                path.write_text(value)
            elif isinstance(value, dict):
                path.mkdir(parents=True, exist_ok=True)

                _create(path, value)

    return _create


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mock_creds() -> MagicMock:
    return MagicMock()


@pytest.fixture
def docx_file(tmp_path: Path, create_files: CreateFiles) -> Path:
    create_files(tmp_path, {
        "doc.docx": None,
    })
    return tmp_path / "doc.docx"


@pytest.fixture
def mock_get_credentials(monkeypatch: MonkeyPatch) -> MagicMock:
    mock = MagicMock(return_value=MagicMock())
    monkeypatch.setattr("goodoc.auth.Auth.get_credentials", mock)
    return mock


@pytest.fixture
def mock_upload(monkeypatch: MonkeyPatch) -> MagicMock:
    mock = MagicMock(return_value="https://docs.google.com/doc")
    monkeypatch.setattr("goodoc.drive.Drive.upload", mock)
    return mock


@pytest.fixture
def mock_browser(monkeypatch: MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    monkeypatch.setattr("goodoc.app.webbrowser.open", mock)
    return mock


@pytest.fixture
def mock_drive_build(monkeypatch: MonkeyPatch) -> MagicMock:
    mock_service = MagicMock()
    mock_service.files.return_value.create.return_value.execute.return_value = {
        "webViewLink": "https://docs.google.com/doc"
    }
    monkeypatch.setattr("goodoc.drive.build", lambda *args, **kwargs: mock_service)
    return mock_service
