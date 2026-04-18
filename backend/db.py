import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from models import ApplicationCreate, ApplicationUpdate, STATUS_RANK

DB_PATH = Path(__file__).parent / "tracker.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                company          TEXT NOT NULL,
                role             TEXT NOT NULL,
                status           TEXT NOT NULL,
                applied_date     DATE,
                last_updated     DATETIME DEFAULT CURRENT_TIMESTAMP,
                source_email_ids TEXT DEFAULT '[]',
                notes            TEXT,
                is_manual        INTEGER DEFAULT 0
            )
        """)
        conn.commit()


def list_applications() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, company, role, status, applied_date, last_updated, notes, is_manual FROM applications ORDER BY last_updated DESC"
        ).fetchall()
    return [dict(r) for r in rows]


def create_application(data: ApplicationCreate) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO applications (company, role, status, applied_date, notes, is_manual)
               VALUES (?, ?, ?, ?, ?, 1)""",
            (data.company, data.role, data.status, str(data.applied_date) if data.applied_date else None, data.notes),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (cur.lastrowid,)).fetchone()
    return dict(row)


def update_application(app_id: int, data: ApplicationUpdate) -> Optional[dict]:
    fields = {k: v for k, v in data.model_dump().items() if v is not None}
    if not fields:
        return get_application(app_id)
    if "applied_date" in fields and fields["applied_date"]:
        fields["applied_date"] = str(fields["applied_date"])
    fields["last_updated"] = datetime.utcnow().isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [app_id]
    with get_conn() as conn:
        conn.execute(f"UPDATE applications SET {set_clause} WHERE id = ?", values)
        conn.commit()
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    return dict(row) if row else None


def delete_application(app_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM applications WHERE id = ?", (app_id,))
        conn.commit()
    return cur.rowcount > 0


def get_application(app_id: int) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM applications WHERE id = ?", (app_id,)).fetchone()
    return dict(row) if row else None


def upsert_from_email(company: str, role: str, status: str, applied_date: Optional[str], email_id: str, email_date: Optional[str] = None):
    """Insert or update an application row discovered via email."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM applications WHERE LOWER(company) = LOWER(?) AND LOWER(role) = LOWER(?)",
            (company, role),
        ).fetchone()

        if row:
            existing_rank = STATUS_RANK.get(row["status"], 0)
            new_rank = STATUS_RANK.get(status, 0)
            try:
                ids = json.loads(row["source_email_ids"] or "[]")
            except json.JSONDecodeError:
                ids = []
            if email_id not in ids:
                ids.append(email_id)

            # Only advance status, never regress
            new_status = status if new_rank >= existing_rank else row["status"]
            last_updated = email_date or datetime.utcnow().strftime("%Y-%m-%d")
            conn.execute(
                """UPDATE applications
                   SET status = ?, source_email_ids = ?, last_updated = ?
                   WHERE id = ?""",
                (new_status, json.dumps(ids), last_updated, row["id"]),
            )
        else:
            last_updated = email_date or datetime.utcnow().strftime("%Y-%m-%d")
            conn.execute(
                """INSERT INTO applications (company, role, status, applied_date, source_email_ids, is_manual, last_updated)
                   VALUES (?, ?, ?, ?, ?, 0, ?)""",
                (company, role, status, applied_date, json.dumps([email_id]), last_updated),
            )
        conn.commit()


def get_processed_email_ids() -> set[str]:
    with get_conn() as conn:
        rows = conn.execute("SELECT source_email_ids FROM applications").fetchall()
    ids: set[str] = set()
    for row in rows:
        ids.update(json.loads(row["source_email_ids"] or "[]"))
    return ids
