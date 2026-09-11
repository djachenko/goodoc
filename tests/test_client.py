import re

from goodoc.client import ACCESS_KEY_HASH, CLIENT_ID, client_config


class TestClientConfig:
    def test_uses_installed_app_section(self) -> None:
        assert set(client_config("key")) == {"installed"}

    def test_carries_bundled_client_id(self) -> None:
        assert client_config("key")["installed"]["client_id"] == CLIENT_ID

    def test_access_key_becomes_client_secret(self) -> None:
        assert client_config("the-key")["installed"]["client_secret"] == "the-key"

    def test_points_at_google_endpoints(self) -> None:
        installed = client_config("key")["installed"]

        assert installed["auth_uri"] == "https://accounts.google.com/o/oauth2/auth"
        assert installed["token_uri"] == "https://oauth2.googleapis.com/token"


class TestAccessKeyHash:
    def test_is_sha256_digest(self) -> None:
        assert re.fullmatch(r"[0-9a-f]{64}", ACCESS_KEY_HASH)
