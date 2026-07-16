import pytest
from unittest.mock import MagicMock, patch

from goodoc.auth import get_credentials
from goodoc.config import Config


@pytest.fixture
def config(tmp_path):
    return Config(goodoc_dir=tmp_path, scopes=[])


class TestGetCredentials:
    def test_no_credentials_runs_wizard(self, config):
        with patch("goodoc.auth.first_run_wizard", return_value="wizard-creds") as wizard:
            result = get_credentials(config)

        wizard.assert_called_once_with(config)
        assert result == "wizard-creds"

    def test_valid_token_loaded_from_file(self, config):
        config.credentials_path.write_text("{}")
        config.token_path.write_text("{}")

        creds = MagicMock(valid=True)

        with patch("goodoc.auth.Credentials.from_authorized_user_file", return_value=creds):
            with patch("goodoc.auth.InstalledAppFlow.from_client_secrets_file") as flow_factory:
                result = get_credentials(config)

        assert result is creds
        creds.refresh.assert_not_called()
        flow_factory.assert_not_called()
        assert config.token_path.read_text() == "{}"

    def test_expired_token_refreshed_and_written(self, config):
        config.credentials_path.write_text("{}")
        config.token_path.write_text("{}")

        refreshed_token = '{"token": "refreshed"}'

        creds = MagicMock(valid=False, expired=True, refresh_token="rt")
        creds.to_json.return_value = refreshed_token

        with patch("goodoc.auth.Credentials.from_authorized_user_file", return_value=creds):
            with patch("goodoc.auth.Request"):
                result = get_credentials(config)

        creds.refresh.assert_called_once()
        assert result is creds
        assert config.token_path.read_text() == refreshed_token

    def test_no_token_runs_flow_and_writes(self, config):
        config.credentials_path.write_text("{}")

        fresh_token = '{"token": "fresh"}'

        new_creds = MagicMock()
        new_creds.to_json.return_value = fresh_token

        flow = MagicMock()
        flow.run_local_server.return_value = new_creds

        with patch("goodoc.auth.InstalledAppFlow.from_client_secrets_file", return_value=flow):
            result = get_credentials(config)

        assert result is new_creds
        assert config.token_path.read_text() == fresh_token
