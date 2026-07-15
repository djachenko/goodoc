from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_creds():
    return MagicMock()


@pytest.fixture
def mock_get_credentials(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("goodoc.main.get_credentials", mock)
    return mock


@pytest.fixture
def mock_upload(monkeypatch):
    mock = MagicMock(return_value="https://docs.google.com/doc")
    monkeypatch.setattr("goodoc.main.upload", mock)
    return mock


@pytest.fixture
def mock_browser(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr("goodoc.main.webbrowser.open", mock)
    return mock


@pytest.fixture
def mock_drive_build(monkeypatch):
    mock_service = MagicMock()
    mock_service.files.return_value.create.return_value.execute.return_value = {
        "webViewLink": "https://docs.google.com/doc"
    }
    monkeypatch.setattr("goodoc.drive.build", lambda *args, **kwargs: mock_service)
    return mock_service
