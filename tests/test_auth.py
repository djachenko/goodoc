from unittest.mock import MagicMock

import pytest

from goodoc.auth import get_credentials
from goodoc.main import Config


@pytest.fixture
def config(tmp_path):
    return Config(goodoc_dir=tmp_path)


class TestGetCredentials:
    def test_no_credentials_runs_wizard(self, config, monkeypatch):
        wizard = MagicMock(return_value="wizard-creds")
        monkeypatch.setattr("goodoc.auth.first_run_wizard", wizard)

        result = get_credentials(config)

        wizard.assert_called_once_with(config)
        assert result == "wizard-creds"

    def test_valid_token_returned_as_is(self, config, monkeypatch):
        config.credentials_path.write_text("{}")
        config.token_path.write_text("{}")

        creds = MagicMock(valid=True)
        monkeypatch.setattr("goodoc.auth.Credentials.from_authorized_user_file", MagicMock(return_value=creds))
        flow_factory = MagicMock()
        monkeypatch.setattr("goodoc.auth.InstalledAppFlow.from_client_secrets_file", flow_factory)

        result = get_credentials(config)

        assert result is creds
        creds.refresh.assert_not_called()
        flow_factory.assert_not_called()
        assert config.token_path.read_text() == "{}"

    def test_expired_token_refreshed_and_written(self, config, monkeypatch):
        config.credentials_path.write_text("{}")
        config.token_path.write_text("{}")

        creds = MagicMock(valid=False, expired=True, refresh_token="rt")
        creds.to_json.return_value = '{"token": "refreshed"}'
        monkeypatch.setattr("goodoc.auth.Credentials.from_authorized_user_file", MagicMock(return_value=creds))
        monkeypatch.setattr("goodoc.auth.Request", MagicMock())

        result = get_credentials(config)

        creds.refresh.assert_called_once()
        assert result is creds
        assert config.token_path.read_text() == '{"token": "refreshed"}'

    def test_no_token_runs_flow_and_writes(self, config, monkeypatch):
        config.credentials_path.write_text("{}")

        new_creds = MagicMock()
        new_creds.to_json.return_value = '{"token": "fresh"}'
        flow = MagicMock()
        flow.run_local_server.return_value = new_creds
        monkeypatch.setattr("goodoc.auth.InstalledAppFlow.from_client_secrets_file", MagicMock(return_value=flow))

        result = get_credentials(config)

        assert result is new_creds
        assert config.token_path.read_text() == '{"token": "fresh"}'
