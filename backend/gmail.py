import base64
import email as email_lib
from email.utils import parsedate_to_datetime
from typing import Generator
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SEARCH_QUERY = "after:2026/02/25"
MAX_RESULTS_PER_PAGE = 100


def fetch_unprocessed_emails(creds: Credentials, already_processed: set[str]) -> Generator[dict, None, None]:
    """Yield dicts with id, subject, body for emails not yet processed."""
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    page_token = None

    while True:
        params = {
            "userId": "me",
            "q": SEARCH_QUERY,
            "maxResults": MAX_RESULTS_PER_PAGE,
        }
        if page_token:
            params["pageToken"] = page_token

        result = service.users().messages().list(**params).execute()
        messages = result.get("messages", [])

        for msg_stub in messages:
            msg_id = msg_stub["id"]
            if msg_id in already_processed:
                continue
            msg = service.users().messages().get(
                userId="me", id=msg_id, format="full"
            ).execute()
            yield _extract(msg)

        page_token = result.get("nextPageToken")
        if not page_token:
            break


def _extract(msg: dict) -> dict:
    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    subject = headers.get("Subject", "")
    date_str = headers.get("Date", "")
    body = _get_body(msg.get("payload", {}))

    parsed_date = None
    if date_str:
        try:
            parsed_date = parsedate_to_datetime(date_str).strftime("%Y-%m-%d")
        except Exception:
            pass

    return {"id": msg["id"], "subject": subject, "date": parsed_date, "body": body[:4000]}


def _get_body(payload: dict) -> str:
    """Recursively extract plain-text body from a Gmail message payload."""
    mime = payload.get("mimeType", "")
    data = payload.get("body", {}).get("data")

    if data and mime == "text/plain":
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")

    for part in payload.get("parts", []):
        text = _get_body(part)
        if text:
            return text

    # Fall back to HTML if no plain text found
    if data and mime == "text/html":
        raw = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        # Strip tags crudely — good enough for LLM context
        import re
        return re.sub(r"<[^>]+>", " ", raw)

    return ""
