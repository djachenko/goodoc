import os
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Self, ClassVar


@dataclass(frozen=True)
class Config:
    goodoc_dir: Path
    scopes: list[str]

    __SCOPES: ClassVar[list[str]] = [
        "https://www.googleapis.com/auth/drive.file",
    ]

    @classmethod
    def default(cls) -> Self:
        app_folder_str = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
        app_folder_path = Path(app_folder_str) / "goodoc"

        return cls(
            goodoc_dir=app_folder_path,
            scopes=cls.__SCOPES
        )

    @cached_property
    def credentials_path(self) -> Path:
        return self.goodoc_dir / "credentials.json"

    @cached_property
    def token_path(self) -> Path:
        return self.goodoc_dir / "token.json"
