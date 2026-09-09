from pathlib import Path

from pytest import MonkeyPatch

from goodoc.config import Config


class TestConfig:
    def test_default_goodoc_dir(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        config = Config.default()

        assert config.goodoc_dir == Path.home() / ".config" / "goodoc"

    def test_xdg_config_home(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        config = Config.default()

        assert config.goodoc_dir == tmp_path / "goodoc"

    def test_credentials_path(self) -> None:
        config = Config(goodoc_dir=Path("/custom"), scopes=[])

        assert config.credentials_path == Path("/custom/credentials.json")

    def test_token_path(self) -> None:
        config = Config(goodoc_dir=Path("/custom"), scopes=[])

        assert config.token_path == Path("/custom/token.json")
