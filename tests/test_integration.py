from collections.abc import Iterator
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner

from conftest import CreateFiles
from goodoc.app import App
from goodoc.main import _create_app, app
from goodoc.setup import Setup


@pytest.fixture
def config_dir(tmp_path: Path, monkeypatch: MonkeyPatch) -> Path:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    return tmp_path / "goodoc"


@pytest.fixture
def goodoc(config_dir: Path, monkeypatch: MonkeyPatch) -> App:
    instance = _create_app()
    monkeypatch.setattr("goodoc.main._app", instance)

    return instance


@pytest.fixture
def authorized(tmp_path: Path, config_dir: Path, create_files: CreateFiles) -> Iterator[None]:
    create_files(tmp_path, {
        "goodoc": {
            "credentials.json": "{}",
            "token.json": "{}",
        },
    })

    with patch(
        "goodoc.auth.Credentials.from_authorized_user_file",
        return_value=MagicMock(valid=True),
    ):
        yield


@pytest.mark.usefixtures("goodoc", "authorized", "mock_drive_build")
class TestUploadEndToEnd:
    def test_uploads_and_opens_browser(
            self,
            runner: CliRunner,
            docx_file: Path,
            mock_drive_build: MagicMock,
            mock_browser: MagicMock,
    ) -> None:
        result = runner.invoke(app, [str(docx_file)])

        _, kwargs = mock_drive_build.files.return_value.create.call_args

        assert result.exit_code == 0
        assert kwargs["body"]["mimeType"] == "application/vnd.google-apps.document"
        assert "https://docs.google.com/doc" in result.stdout
        mock_browser.assert_called_once_with("https://docs.google.com/doc")

    def test_no_open_flag_skips_browser(
            self,
            runner: CliRunner,
            docx_file: Path,
            mock_browser: MagicMock,
    ) -> None:
        result = runner.invoke(app, [str(docx_file), "--no-open"])

        assert result.exit_code == 0
        mock_browser.assert_not_called()

    def test_unsupported_format_stops_before_upload(
            self,
            runner: CliRunner,
            tmp_path: Path,
            create_files: CreateFiles,
            mock_drive_build: MagicMock,
    ) -> None:
        create_files(tmp_path, {
            "notes.txt": None,
        })

        result = runner.invoke(app, [str(tmp_path / "notes.txt")])

        assert result.exit_code == 1
        mock_drive_build.files.return_value.create.assert_not_called()


class TestAuthEndToEnd:
    def test_login_without_credentials_runs_wizard(
            self,
            runner: CliRunner,
            goodoc: App,
            config_dir: Path,
    ) -> None:
        creds = MagicMock()
        creds.to_json.return_value = '{"token": "wizard"}'

        with patch.object(Setup, "first_run_wizard", return_value=creds) as wizard:
            result = runner.invoke(app, ["login"])

        wizard.assert_called_once()
        assert result.exit_code == 0
        assert (config_dir / "token.json").read_text() == '{"token": "wizard"}'

    def test_logout_removes_stored_token(
            self,
            runner: CliRunner,
            goodoc: App,
            config_dir: Path,
            authorized: None,
    ) -> None:
        result = runner.invoke(app, ["logout"])

        assert result.exit_code == 0
        assert not (config_dir / "token.json").exists()

    def test_logout_without_token_reports_state(self, runner: CliRunner, goodoc: App) -> None:
        result = runner.invoke(app, ["logout"])

        assert result.exit_code == 0
        assert "Not logged in." in result.stdout
