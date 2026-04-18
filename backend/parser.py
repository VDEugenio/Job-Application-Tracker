import json
import os
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


SYSTEM_PROMPT = """You are an email classifier for a job application tracker.

Given an email's subject and body, determine if it is related to a job application the sender submitted.
Job-related emails include: application confirmations, recruiter outreach replies, interview invitations,
offer letters, rejection notices, and follow-up emails from employers.

Do NOT classify as job-related: newsletters, LinkedIn notifications, job alert digests, cold recruiter spam
where the person has not applied, or unrelated emails.

Return ONLY valid JSON with these exact fields:
{
  "is_job_related": true or false,
  "company": "Company Name or null",
  "role": "Job Title or null",
  "status": "Applied" | "Interviewing" | "Offer Received" | "Rejected" | "No Response" | null,
  "applied_date": "YYYY-MM-DD or null"
}

Status rules:
- "Applied": application received / confirmation
- "Interviewing": phone screen, interview scheduled, technical assessment invited
- "Offer Received": offer letter or verbal offer
- "Rejected": rejection or "not moving forward"
- "No Response": if unclear but job-related
If is_job_related is false, set all other fields to null."""


def _parse_json(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    # Extract the first complete JSON object (non-greedy, brace-balanced)
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        return json.loads(raw[start:end])
    except (ValueError, json.JSONDecodeError):
        return None


def classify_email(email_id: str, subject: str, body: str) -> dict | None:
    """Returns a dict with company/role/status/applied_date, or None if not job-related."""
    client = _get_client()
    content = f"Subject: {subject}\n\nBody:\n{body}"

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": content}],
    )

    raw = response.content[0].text.strip()
    data = _parse_json(raw)
    if data is None or not data.get("is_job_related"):
        return None

    return {
        "company": data.get("company"),
        "role": data.get("role"),
        "status": data.get("status") or "No Response",
        "applied_date": data.get("applied_date"),
    }
