import json
import os
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = Path(__file__).parent / "credentials.json"
TOKEN_FILE = Path(__file__).parent / "token.json"
REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI", "http://localhost:8001/auth/callback")

# Keyed by OAuth state value so concurrent login attempts don't overwrite each other
# and so the state parameter is validated on callback (prevents CSRF)
_pending_flows: dict[str, Flow] = {}


def credentials_file_exists() -> bool:
    return CREDENTIALS_FILE.exists()


def get_valid_credentials() -> Credentials | None:
    if not TOKEN_FILE.exists():
        return None
    creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_token(creds)
    return creds if creds and creds.valid else None


def get_auth_url() -> str:
    flow = Flow.from_client_secrets_file(
        str(CREDENTIALS_FILE),
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )
    url, state = flow.authorization_url(prompt="consent", access_type="offline")
    _pending_flows[state] = flow
    return url


def handle_callback(code: str, state: str) -> Credentials:
    flow = _pending_flows.pop(state, None)
    if flow is None:
        raise ValueError("Invalid or expired OAuth state. Please try connecting again.")
    flow.fetch_token(code=code)
    creds = flow.credentials
    _save_token(creds)
    return creds


def _save_token(creds: Credentials):
    TOKEN_FILE.write_text(
        json.dumps({
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": list(creds.scopes or []),
        })
    )
