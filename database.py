"""
database.py
Minimal SQLite wrapper for storing scan history. Kept separate from app.py
so the schema/queries live in one place.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "devfix.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            scan_json TEXT NOT NULL,
            issues_json TEXT NOT NULL,
            issue_count INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_scan(scan_result, issues):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO scans (timestamp, scan_json, issues_json, issue_count) VALUES (?, ?, ?, ?)",
        (
            datetime.utcnow().isoformat(),
            json.dumps(scan_result),
            json.dumps(issues),
            len(issues),
        ),
    )
    conn.commit()
    scan_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return scan_id


def get_history(limit=10):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, timestamp, issue_count FROM scans ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_scan_by_id(scan_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
    conn.close()
    if row is None:
        return None
    result = dict(row)
    result["scan_json"] = json.loads(result["scan_json"])
    result["issues_json"] = json.loads(result["issues_json"])
    return result
