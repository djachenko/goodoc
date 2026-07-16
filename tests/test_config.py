from pathlib import Path

from goodoc.config import Config


class TestConfig:
    def test_default_goodoc_dir(self, monkeypatch):
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        config = Config.default()

        assert config.goodoc_dir == Path.home() / ".config" / "goodoc"

    def test_xdg_config_home(self, monkeypatch, tmp_path):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        config = Config.default()

        assert config.goodoc_dir == tmp_path / "goodoc"

    def test_credentials_path(self):
        config = Config(goodoc_dir=Path("/custom"), scopes=[])

        assert config.credentials_path == Path("/custom/credentials.json")

    def test_token_path(self):
        config = Config(goodoc_dir=Path("/custom"), scopes=[])

        assert config.token_path == Path("/custom/token.json")
