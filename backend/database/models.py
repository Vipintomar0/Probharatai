"""Database models for ProBharatAI using SQLite + SQLAlchemy."""
import sqlite3
from datetime import datetime
from pathlib import Path
from config import DATA_DIR

DB_PATH = DATA_DIR / "probharatai.db"


def get_connection():
    """Get a SQLite database connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Initialize the database with all required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            plan TEXT,
            result TEXT,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)

    # Task steps table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            step_number INTEGER NOT NULL,
            description TEXT NOT NULL,
            tool TEXT,
            status TEXT DEFAULT 'pending',
            result TEXT,
            error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)

    # Job applications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            platform TEXT NOT NULL,
            company TEXT,
            title TEXT,
            url TEXT,
            status TEXT DEFAULT 'found',
            match_score REAL,
            applied_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)

    # Logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT DEFAULT 'INFO',
            source TEXT,
            message TEXT NOT NULL,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Settings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # API keys table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL UNIQUE,
            api_key TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Approval queue
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            action_description TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            approved_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)

    conn.commit()
    conn.close()


# ── CRUD helpers ──

def create_task(prompt):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (prompt) VALUES (?)", (prompt,))
    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id


def update_task(task_id, **fields):
    conn = get_connection()
    sets = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [task_id]
    conn.execute(f"UPDATE tasks SET {sets}, updated_at = CURRENT_TIMESTAMP WHERE id = ?", values)
    conn.commit()
    conn.close()


def get_task(task_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_tasks(limit=50):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_task_step(task_id, step_number, description, tool=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO task_steps (task_id, step_number, description, tool) VALUES (?, ?, ?, ?)",
        (task_id, step_number, description, tool),
    )
    step_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return step_id


def update_task_step(step_id, **fields):
    conn = get_connection()
    sets = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [step_id]
    conn.execute(f"UPDATE task_steps SET {sets} WHERE id = ?", values)
    conn.commit()
    conn.close()


def get_task_steps(task_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM task_steps WHERE task_id = ? ORDER BY step_number", (task_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_job_application(**fields):
    conn = get_connection()
    keys = ", ".join(fields.keys())
    placeholders = ", ".join("?" for _ in fields)
    conn.execute(f"INSERT INTO job_applications ({keys}) VALUES ({placeholders})", list(fields.values()))
    conn.commit()
    conn.close()


def get_job_applications(task_id=None, limit=100):
    conn = get_connection()
    if task_id:
        rows = conn.execute(
            "SELECT * FROM job_applications WHERE task_id = ? ORDER BY created_at DESC LIMIT ?",
            (task_id, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM job_applications ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_log(message, level="INFO", source=None, details=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO logs (level, source, message, details) VALUES (?, ?, ?, ?)",
        (level, source, message, details),
    )
    conn.commit()
    conn.close()


def get_logs(limit=100, level=None):
    conn = get_connection()
    if level:
        rows = conn.execute(
            "SELECT * FROM logs WHERE level = ? ORDER BY created_at DESC LIMIT ?", (level, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM logs ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def set_setting(key, value):
    conn = get_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (key, value, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
        (key, value),
    )
    conn.commit()
    conn.close()


def get_setting(key, default=None):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def save_api_key(provider, api_key):
    conn = get_connection()
    conn.execute(
        """INSERT INTO api_keys (provider, api_key, updated_at)
           VALUES (?, ?, CURRENT_TIMESTAMP)
           ON CONFLICT(provider) DO UPDATE SET api_key = ?, updated_at = CURRENT_TIMESTAMP""",
        (provider, api_key, api_key),
    )
    conn.commit()
    conn.close()


def get_api_key(provider):
    conn = get_connection()
    row = conn.execute("SELECT api_key FROM api_keys WHERE provider = ? AND is_active = 1", (provider,)).fetchone()
    conn.close()
    return row["api_key"] if row else None


def create_approval(task_id, action_description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO approvals (task_id, action_description) VALUES (?, ?)",
        (task_id, action_description),
    )
    approval_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return approval_id


def resolve_approval(approval_id, status, approved_by="ui"):
    conn = get_connection()
    conn.execute(
        "UPDATE approvals SET status = ?, approved_by = ?, resolved_at = CURRENT_TIMESTAMP WHERE id = ?",
        (status, approved_by, approval_id),
    )
    conn.commit()
    conn.close()


def get_pending_approvals():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM approvals WHERE status = 'pending' ORDER BY created_at").fetchall()
    conn.close()
    return [dict(r) for r in rows]
