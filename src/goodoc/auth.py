import hashlib

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from goodoc.client import ACCESS_KEY_HASH
from goodoc.config import Config
from goodoc.setup import authorize_shared, first_run_wizard


class Auth:
    @staticmethod
    def get_credentials(config: Config) -> Credentials:
        creds = None

        if config.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(config.token_path), config.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds = Auth._authorize(config)

            Auth._save(config, creds)

        return creds

    @staticmethod
    def login_shared(config: Config, access_key: str) -> Credentials:
        if hashlib.sha256(access_key.encode()).hexdigest() != ACCESS_KEY_HASH:
            raise ValueError("Invalid access key.")

        creds = authorize_shared(config, access_key)
        Auth._save(config, creds)

        return creds

    @staticmethod
    def _authorize(config: Config) -> Credentials:
        if config.credentials_path.exists():
            flow = InstalledAppFlow.from_client_secrets_file(str(config.credentials_path), config.scopes)

            return flow.run_local_server(port=0)

        return first_run_wizard(config)

    @staticmethod
    def _save(config: Config, creds: Credentials) -> None:
        config.token_path.parent.mkdir(parents=True, exist_ok=True)

        with config.token_path.open("w") as f:
            f.write(creds.to_json())
