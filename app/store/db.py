import sqlite3
from app.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    job_id TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    link TEXT,
    applied_at TEXT,
    status TEXT,
    simplified_jd TEXT,
    resume_file TEXT,
    screenshot_path TEXT
);
"""

def init_db():
    conn = sqlite3.connect(settings.DB_PATH)
    cur = conn.cursor()
    cur.execute(SCHEMA)
    conn.commit()
    conn.close()
