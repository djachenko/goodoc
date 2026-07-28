from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner


@pytest.fixture
def create_files():
    def _create(root: Path, structure: dict):
        for key, value in structure.items():
            path = root / key

            if value is None:
                path.touch()
            elif isinstance(value, dict):
                path.mkdir(parents=True, exist_ok=True)
                _create(path, value)

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
