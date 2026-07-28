import hashlib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from goodoc.client import ACCESS_KEY_HASH
from goodoc.config import Config
from goodoc.setup import Setup


class Auth:
    def __init__(self, config: Config, setup: Setup) -> None:
        self.config = config
        self._setup = setup

    def get_credentials(self) -> Credentials:
        creds = None

        if self.config.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.config.token_path), self.config.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds = self._authorize()

            self._save(creds)

        return creds

    def login_shared(self, access_key: str) -> Credentials:
        if hashlib.sha256(access_key.encode()).hexdigest() != ACCESS_KEY_HASH:
            raise ValueError("Invalid access key.")

        creds = self._setup.authorize_shared(access_key)
        self._save(creds)

        return creds

    def _authorize(self) -> Credentials:
        if self.config.credentials_path.exists():
            flow = InstalledAppFlow.from_client_secrets_file(str(self.config.credentials_path), self.config.scopes)

            return flow.run_local_server(port=0)

        return self._setup.first_run_wizard()

    def _save(self, creds: Credentials) -> None:
        self.config.token_path.parent.mkdir(parents=True, exist_ok=True)

        with self.config.token_path.open("w") as f:
            f.write(creds.to_json())
