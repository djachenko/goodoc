from pathlib import Path

import pytest
import typer
from unittest.mock import MagicMock

from goodoc.app import App
from goodoc.auth import Auth
from goodoc.config import Config
from goodoc.drive import Drive


@pytest.fixture
def config(tmp_path):
    return Config(goodoc_dir=tmp_path, scopes=[])


@pytest.fixture
def mock_auth():
    return MagicMock(spec=Auth)


@pytest.fixture
def mock_drive():
    mock = MagicMock(spec=Drive)
    mock.upload.return_value = "https://docs.google.com/doc"
    return mock


@pytest.fixture
def app(config, mock_auth, mock_drive):
    return App(config, mock_auth, mock_drive)


class TestValidateFile:
    def test_returns_none_on_valid_file(self, docx_file):
        assert App.validate(docx_file) is None

    def test_returns_error_on_missing_file(self):
        assert App.validate(Path("missing.docx")) is not None

    def test_returns_error_on_unsupported_format(self, tmp_path, create_files):
        create_files(tmp_path, {"data.txt": None})

        assert App.validate(tmp_path / "data.txt") is not None

    def test_missing_takes_priority_over_format(self):
        assert App.validate(Path("missing.txt")) is not None


class TestUpload:
    def test_uploads_file(self, app, mock_drive, docx_file):
        app.upload([docx_file], open_browser=False)

        mock_drive.upload.assert_called_once_with(docx_file)

    def test_uploads_each_file(self, app, mock_drive, tmp_path, create_files):
        create_files(tmp_path, {"a.docx": None, "b.docx": None})
        files = [tmp_path / "a.docx", tmp_path / "b.docx"]

        app.upload(files, open_browser=False)

        assert mock_drive.upload.call_count == 2

    def test_opens_browser(self, app, mock_drive, docx_file, mock_browser):
        app.upload([docx_file], open_browser=True)

        mock_browser.assert_called_once_with("https://docs.google.com/doc")

    def test_skips_browser(self, app, mock_drive, docx_file, mock_browser):
        app.upload([docx_file], open_browser=False)

        mock_browser.assert_not_called()

    def test_missing_file_exits(self, app, mock_drive):
        with pytest.raises(typer.Exit):
            app.upload([Path("missing.docx")], open_browser=False)

        mock_drive.upload.assert_not_called()

    def test_validates_all_before_uploading(self, app, mock_drive, docx_file):
        with pytest.raises(typer.Exit):
            app.upload([docx_file, Path("missing.docx")], open_browser=False)

        mock_drive.upload.assert_not_called()


class TestLogin:
    def test_no_key_calls_get_credentials(self, app, mock_auth):
        app.login()

        mock_auth.get_credentials.assert_called_once()

    def test_key_calls_login_shared(self, app, mock_auth):
        app.login(key="my-key")

        mock_auth.login_shared.assert_called_once_with("my-key")

    def test_invalid_key_exits(self, app, mock_auth):
        mock_auth.login_shared.side_effect = ValueError("Invalid access key.")

        with pytest.raises(typer.Exit):
            app.login(key="wrong")


class TestLogout:
    def test_removes_token(self, app, config):
        config.token_path.parent.mkdir(parents=True, exist_ok=True)
        config.token_path.write_text("{}")

        app.logout()

        assert not config.token_path.exists()

    def test_no_token_no_error(self, app):
        app.logout()
