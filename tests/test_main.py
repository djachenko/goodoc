from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest import MonkeyPatch
from typer.testing import CliRunner

from goodoc.app import App
from goodoc.main import app


@pytest.fixture
def mock_app(monkeypatch: MonkeyPatch) -> MagicMock:
    mock = MagicMock(spec=App)
    monkeypatch.setattr("goodoc.main._app", mock)
    return mock


class TestCLI:
    def test_upload_is_default_command(
            self,
            runner: CliRunner,
            mock_app: MagicMock,
            docx_file: Path,
    ) -> None:
        runner.invoke(app, [str(docx_file)])

        mock_app.upload.assert_called_once()

    def test_open_browser_by_default(
            self,
            runner: CliRunner,
            mock_app: MagicMock,
            docx_file: Path,
    ) -> None:
        runner.invoke(app, [str(docx_file)])

        mock_app.upload.assert_called_once_with([docx_file], open_browser=True)

    def test_no_open_flag(self, runner: CliRunner, mock_app: MagicMock, docx_file: Path) -> None:
        runner.invoke(app, [str(docx_file), "--no-open"])

        mock_app.upload.assert_called_once_with([docx_file], open_browser=False)

    def test_login_command(self, runner: CliRunner, mock_app: MagicMock) -> None:
        runner.invoke(app, ["login"])

        mock_app.login.assert_called_once_with(None)

    def test_login_with_key(self, runner: CliRunner, mock_app: MagicMock) -> None:
        runner.invoke(app, ["login", "--key", "abc"])

        mock_app.login.assert_called_once_with("abc")

    def test_logout_command(self, runner: CliRunner, mock_app: MagicMock) -> None:
        runner.invoke(app, ["logout"])

        mock_app.logout.assert_called_once()
