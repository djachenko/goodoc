import hashlib
from unittest.mock import MagicMock, patch

import pytest

from goodoc.auth import Auth
from goodoc.config import Config
from goodoc.setup import Setup


@pytest.fixture
def config(tmp_path):
    return Config(goodoc_dir=tmp_path, scopes=[])


@pytest.fixture
def mock_setup():
    return MagicMock(spec=Setup)


@pytest.fixture
def auth(config, mock_setup):
    return Auth(config, mock_setup)


class TestGetCredentials:
    def test_no_credentials_runs_wizard(self, auth, mock_setup):
        wizard_creds = MagicMock()
        wizard_creds.to_json.return_value = "{}"
        mock_setup.first_run_wizard.return_value = wizard_creds

        result = auth.get_credentials()

        mock_setup.first_run_wizard.assert_called_once()
        assert result is wizard_creds

    def test_valid_token_loaded_from_file(self, auth, config):
        config.credentials_path.write_text("{}")
        config.token_path.write_text("{}")

        creds = MagicMock(valid=True)

        with (
            patch("goodoc.auth.Credentials.from_authorized_user_file", return_value=creds),
            patch("goodoc.auth.InstalledAppFlow.from_client_secrets_file") as flow_factory,
        ):
            result = auth.get_credentials()

        assert result is creds
        creds.refresh.assert_not_called()
        flow_factory.assert_not_called()
        assert config.token_path.read_text() == "{}"

    def test_expired_token_refreshed_and_written(self, auth, config):
        config.credentials_path.write_text("{}")
        config.token_path.write_text("{}")

        refreshed_token = '{"token": "refreshed"}'

        creds = MagicMock(valid=False, expired=True, refresh_token="rt")
        creds.to_json.return_value = refreshed_token

        with (
            patch("goodoc.auth.Credentials.from_authorized_user_file", return_value=creds),
            patch("goodoc.auth.Request"),
        ):
            result = auth.get_credentials()

        creds.refresh.assert_called_once()
        assert result is creds
        assert config.token_path.read_text() == refreshed_token

    def test_no_token_runs_flow_and_writes(self, auth, config):
        config.credentials_path.write_text("{}")

        fresh_token = '{"token": "fresh"}'

        new_creds = MagicMock()
        new_creds.to_json.return_value = fresh_token

        flow = MagicMock()
        flow.run_local_server.return_value = new_creds

        with patch("goodoc.auth.InstalledAppFlow.from_client_secrets_file", return_value=flow):
            result = auth.get_credentials()

        assert result is new_creds
        assert config.token_path.read_text() == fresh_token


class TestLoginShared:
    def test_invalid_key_rejected(self, auth, mock_setup):
        with pytest.raises(ValueError):
            auth.login_shared("wrong-key")

        mock_setup.authorize_shared.assert_not_called()

    def test_valid_key_authorizes_and_writes(self, auth, config, mock_setup):
        shared_token = '{"token": "shared"}'

        creds = MagicMock()
        creds.to_json.return_value = shared_token
        mock_setup.authorize_shared.return_value = creds

        with patch("goodoc.auth.ACCESS_KEY_HASH", _sha256("right-key")):
            result = auth.login_shared("right-key")

        mock_setup.authorize_shared.assert_called_once_with("right-key")
        assert result is creds
        assert config.token_path.read_text() == shared_token


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
