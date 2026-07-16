from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from goodoc.config import Config
from goodoc.setup import first_run_wizard


def get_credentials(config: Config) -> Credentials:
    if not config.credentials_path.exists():
        return first_run_wizard(config)

    config.token_path.parent.mkdir(parents=True, exist_ok=True)

    creds = None

    if config.token_path.exists():
        creds = Credentials.from_authorized_user_file(str(config.token_path), config.scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(config.credentials_path), config.scopes)
            creds = flow.run_local_server(port=0)

        with config.token_path.open("w") as f:
            f.write(creds.to_json())

    return creds
