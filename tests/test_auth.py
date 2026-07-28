import pytest
from unittest.mock import MagicMock, patch

from goodoc.auth import Auth
from goodoc.config import Config


@pytest.fixture
def config(tmp_path):
    return Config(goodoc_dir=tmp_path, scopes=[])


class TestGetCredentials:
    def test_no_credentials_runs_wizard(self, config):
        wizard_creds = MagicMock()
        wizard_creds.to_json.return_value = "{}"

        with patch("goodoc.auth.first_run_wizard", return_value=wizard_creds) as wizard:
            result = Auth.get_credentials(config)

        wizard.assert_called_once_with(config)
        assert result is wizard_creds

    def test_valid_token_loaded_from_file(self, config):
        config.credentials_path.write_text("{}")
        config.token_path.write_text("{}")

        creds = MagicMock(valid=True)

        with patch("goodoc.auth.Credentials.from_authorized_user_file", return_value=creds):
            with patch("goodoc.auth.InstalledAppFlow.from_client_secrets_file") as flow_factory:
                result = Auth.get_credentials(config)

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
                result = Auth.get_credentials(config)

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
            result = Auth.get_credentials(config)

        assert result is new_creds
        assert config.token_path.read_text() == fresh_token


class TestLoginShared:
    def test_invalid_key_rejected(self, config):
        with patch("goodoc.auth.authorize_shared") as shared:
            with pytest.raises(ValueError):
                Auth.login_shared(config, "wrong-key")

        shared.assert_not_called()
        assert not config.token_path.exists()

    def test_valid_key_authorizes_and_writes(self, config):
        shared_token = '{"token": "shared"}'

        creds = MagicMock()
        creds.to_json.return_value = shared_token

        with patch("goodoc.auth.authorize_shared", return_value=creds) as shared:
            with patch("goodoc.auth.ACCESS_KEY_HASH", _sha256("right-key")):
                result = Auth.login_shared(config, "right-key")

        shared.assert_called_once_with(config, "right-key")
        assert result is creds
        assert config.token_path.read_text() == shared_token


def _sha256(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode()).hexdigest()
