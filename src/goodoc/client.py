CLIENT_ID = "107871228272-0ik0igaudebbqco44gatgfrok469jhiq.apps.googleusercontent.com"

ACCESS_KEY_HASH = "b5fe8c482ec4140dcd9a1d181e0400dbf798e41b5c369c3586cc8acbfe923d0c"


def client_config(access_key: str) -> dict[str, dict[str, str]]:
    return {
        "installed": {
            "client_id": CLIENT_ID,
            "client_secret": access_key,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
