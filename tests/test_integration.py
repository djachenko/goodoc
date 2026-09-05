from unittest.mock import MagicMock, patch

import pytest

from goodoc.app import App
from goodoc.auth import Auth
from goodoc.drive import Drive
from goodoc.main import _create_app, app
from goodoc.setup import Setup


@pytest.fixture
def config_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    return tmp_path / "goodoc"


@pytest.fixture
def goodoc(config_dir, monkeypatch):
    instance = _create_app()
    monkeypatch.setattr("goodoc.main._app", instance)

    return instance


@pytest.fixture
def authorized(config_dir):
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "credentials.json").write_text("{}")
    (config_dir / "token.json").write_text("{}")

    with patch("goodoc.auth.Credentials.from_authorized_user_file", return_value=MagicMock(valid=True)):
        yield


class TestWiring:
    def test_builds_full_dependency_graph(self, goodoc):
        assert isinstance(goodoc, App)
        assert isinstance(goodoc._drive, Drive)
        assert isinstance(goodoc._drive._auth, Auth)
        assert isinstance(goodoc._drive._auth._setup, Setup)

    def test_shares_single_config(self, goodoc):
        assert goodoc._config is goodoc._auth._config
        assert goodoc._config is goodoc._drive._auth._config

    def test_config_points_at_xdg_dir(self, goodoc, config_dir):
        assert goodoc._config.goodoc_dir == config_dir


@pytest.mark.usefixtures("goodoc", "authorized", "mock_drive_build")
class TestUploadEndToEnd:
    def test_uploads_and_opens_browser(self, runner, docx_file, mock_drive_build, mock_browser):
        result = runner.invoke(app, [str(docx_file)])

        _, kwargs = mock_drive_build.files.return_value.create.call_args

        assert result.exit_code == 0
        assert kwargs["body"]["mimeType"] == "application/vnd.google-apps.document"
        assert "https://docs.google.com/doc" in result.stdout
        mock_browser.assert_called_once_with("https://docs.google.com/doc")

    def test_no_open_flag_skips_browser(self, runner, docx_file, mock_browser):
        result = runner.invoke(app, [str(docx_file), "--no-open"])

        assert result.exit_code == 0
        mock_browser.assert_not_called()

    def test_unsupported_format_stops_before_upload(self, runner, tmp_path, create_files, mock_drive_build):
        create_files(tmp_path, {"notes.txt": None})

        result = runner.invoke(app, [str(tmp_path / "notes.txt")])

        assert result.exit_code == 1
        mock_drive_build.files.return_value.create.assert_not_called()


class TestAuthEndToEnd:
    def test_login_without_credentials_runs_wizard(self, runner, goodoc, config_dir):
        creds = MagicMock()
        creds.to_json.return_value = '{"token": "wizard"}'

        with patch.object(Setup, "first_run_wizard", return_value=creds) as wizard:
            result = runner.invoke(app, ["login"])

        wizard.assert_called_once()
        assert result.exit_code == 0
        assert (config_dir / "token.json").read_text() == '{"token": "wizard"}'

    def test_logout_removes_stored_token(self, runner, goodoc, config_dir, authorized):
        result = runner.invoke(app, ["logout"])

        assert result.exit_code == 0
        assert not (config_dir / "token.json").exists()

    def test_logout_without_token_reports_state(self, runner, goodoc):
        result = runner.invoke(app, ["logout"])

        assert result.exit_code == 0
        assert "Not logged in." in result.stdout
