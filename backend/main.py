import os
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import db
import auth
import gmail
import parser as email_parser
from models import ApplicationCreate, ApplicationUpdate, VALID_STATUSES

load_dotenv()

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5174")
_CORS_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174",
).split(",")

app = FastAPI(title="Job Application Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_CORS_ORIGINS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

db.init_db()


# ── Applications ─────────────────────────────────────────────────────────────

@app.get("/applications")
def list_applications():
    return db.list_applications()


@app.post("/applications", status_code=201)
def create_application(data: ApplicationCreate):
    if data.status not in VALID_STATUSES:
        raise HTTPException(400, f"Invalid status.")
    return db.create_application(data)


@app.put("/applications/{app_id}")
def update_application(app_id: int, data: ApplicationUpdate):
    if data.status and data.status not in VALID_STATUSES:
        raise HTTPException(400, "Invalid status.")
    result = db.update_application(app_id, data)
    if not result:
        raise HTTPException(404, "Application not found")
    return result


@app.delete("/applications/{app_id}", status_code=204)
def delete_application(app_id: int):
    if not db.delete_application(app_id):
        raise HTTPException(404, "Application not found")
    return Response(status_code=204)


# ── Sync ──────────────────────────────────────────────────────────────────────

@app.post("/sync")
def sync_emails():
    creds = auth.get_valid_credentials()
    if not creds:
        raise HTTPException(401, "Gmail not connected.")

    processed = db.get_processed_email_ids()
    added = 0
    updated = 0
    skipped = 0
    total = 0

    for email in gmail.fetch_unprocessed_emails(creds, processed):
        total += 1
        print(f"[sync] #{total} | subject: {email['subject'][:60]!r}", flush=True)
        try:
            result = email_parser.classify_email(email["id"], email["subject"], email["body"])
        except Exception as e:
            print(f"[sync]   → ERROR classifying email: {e}", flush=True)
            skipped += 1
            continue

        if result is None:
            skipped += 1
            print(f"[sync]   → not job-related (skip)", flush=True)
            continue

        company = result["company"]
        role = result["role"]
        if not company or not role:
            skipped += 1
            print(f"[sync]   → missing company/role (skip)", flush=True)
            continue

        print(f"[sync]   → {company} | {role} | {result['status']}", flush=True)
        existing = next(
            (a for a in db.list_applications()
             if a["company"].lower() == company.lower() and a["role"].lower() == role.lower()),
            None,
        )
        db.upsert_from_email(company, role, result["status"], result["applied_date"], email["id"], email_date=email["date"])
        if existing:
            updated += 1
        else:
            added += 1

    return {"added": added, "updated": updated, "skipped": skipped}


# ── Auth ──────────────────────────────────────────────────────────────────────

@app.get("/auth/status")
def auth_status():
    if not auth.credentials_file_exists():
        return {"connected": False, "reason": "credentials not configured"}
    creds = auth.get_valid_credentials()
    return {"connected": creds is not None}


@app.get("/auth/login")
def auth_login():
    if not auth.credentials_file_exists():
        raise HTTPException(400, "Gmail credentials not configured.")
    return {"url": auth.get_auth_url()}


@app.get("/auth/callback")
def auth_callback(code: str, state: str):
    try:
        auth.handle_callback(code, state)
    except ValueError as e:
        raise HTTPException(400, str(e))
    return RedirectResponse(f"{FRONTEND_URL}/?auth=success")
