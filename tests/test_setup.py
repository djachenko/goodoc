import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import typer

from goodoc.config import Config
from goodoc.setup import Setup


@pytest.fixture
def config(tmp_path):
    return Config(goodoc_dir=tmp_path / "goodoc", scopes=["scope"])


@pytest.fixture
def setup(config):
    return Setup(config)


@pytest.fixture
def source_credentials(tmp_path, create_files):
    create_files(tmp_path, {"downloaded.json": None})
    source = tmp_path / "downloaded.json"
    source.write_text('{"installed": {}}')

    return source


@pytest.fixture
def downloads(tmp_path, monkeypatch, create_files):
    create_files(tmp_path, {"home": {"Downloads": {}}})
    monkeypatch.setattr(Path, "home", lambda: tmp_path / "home")

    return tmp_path / "home" / "Downloads"


@pytest.fixture
def mock_prompt():
    with patch("goodoc.setup.typer.prompt") as prompt:
        yield prompt


@pytest.fixture(autouse=True)
def mock_setup_browser():
    with patch("goodoc.setup.webbrowser.open") as browser:
        yield browser


class TestAuthorizeShared:
    def test_builds_flow_from_shared_client(self, setup, config):
        creds = MagicMock()
        flow = MagicMock()
        flow.run_local_server.return_value = creds

        with patch("goodoc.setup.InstalledAppFlow.from_client_config", return_value=flow) as flow_factory:
            result = setup.authorize_shared("the-key")

        client_config, scopes = flow_factory.call_args.args

        assert client_config["installed"]["client_secret"] == "the-key"
        assert scopes == config.scopes
        assert result is creds


class TestFirstRunWizard:
    def test_non_tty_exits(self, setup):
        with patch("goodoc.setup.sys.stdin.isatty", return_value=False), pytest.raises(typer.Exit) as exc_info:
            setup.first_run_wizard()

        assert exc_info.value.exit_code == 1

    def test_acquires_credentials_then_runs_flow(self, setup, config):
        creds = MagicMock()
        flow = MagicMock()
        flow.run_local_server.return_value = creds

        with (
            patch("goodoc.setup.sys.stdin.isatty", return_value=True),
            patch.object(Setup, "_acquire_credentials") as acquire,
            patch("goodoc.setup.InstalledAppFlow.from_client_secrets_file", return_value=flow) as flow_factory,
        ):
            result = setup.first_run_wizard()

        acquire.assert_called_once()
        flow_factory.assert_called_once_with(str(config.credentials_path), config.scopes)
        assert result is creds


class TestAcquireCredentials:
    def test_copies_entered_file_to_config(self, setup, config, mock_prompt, source_credentials):
        mock_prompt.return_value = str(source_credentials)

        setup._acquire_credentials()

        assert config.credentials_path.read_text() == '{"installed": {}}'

    def test_opens_console_in_browser(self, setup, mock_prompt, mock_setup_browser, source_credentials):
        mock_prompt.return_value = str(source_credentials)

        setup._acquire_credentials()

        mock_setup_browser.assert_called_once()

    def test_missing_file_reprompts(self, setup, config, mock_prompt, tmp_path, source_credentials):
        mock_prompt.side_effect = [str(tmp_path / "nope.json"), str(source_credentials)]

        setup._acquire_credentials()

        assert mock_prompt.call_count == 2
        assert config.credentials_path.exists()

    def test_empty_input_takes_suggestion(self, setup, config, mock_prompt, downloads):
        suggested = downloads / "client_secret_1.json"
        suggested.write_text('{"suggested": true}')
        mock_prompt.return_value = ""

        setup._acquire_credentials()

        assert config.credentials_path.read_text() == '{"suggested": true}'

    def test_empty_input_without_suggestion_reprompts(self, setup, mock_prompt, downloads, source_credentials):
        mock_prompt.side_effect = ["", str(source_credentials)]

        setup._acquire_credentials()

        assert mock_prompt.call_count == 2


class TestLatestDownload:
    def test_returns_none_when_nothing_downloaded(self, setup, downloads):
        assert setup._latest_download() is None

    def test_ignores_unrelated_files(self, setup, downloads):
        (downloads / "report.json").touch()

        assert setup._latest_download() is None

    def test_returns_most_recent(self, setup, downloads):
        older = downloads / "client_secret_old.json"
        newer = downloads / "client_secret_new.json"

        older.touch()
        newer.touch()
        os.utime(older, (1, 1))

        assert setup._latest_download() == newer
