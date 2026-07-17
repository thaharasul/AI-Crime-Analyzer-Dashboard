

import sqlite3
from contextlib import contextmanager

from config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def db_cursor(commit=False):
    """Small helper so routes/services don't repeat connect/close logic."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        if commit:
            conn.commit()
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS crimes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crime_type TEXT NOT NULL,
    category TEXT NOT NULL,
    date_reported TEXT NOT NULL,
    time_reported TEXT NOT NULL,
    zone TEXT NOT NULL,
    location_name TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    severity TEXT NOT NULL,
    weapon_involved INTEGER NOT NULL DEFAULT 0,
    victim_age INTEGER,
    victim_gender TEXT,
    day_of_week TEXT NOT NULL,
    hour_of_day INTEGER NOT NULL,
    description TEXT
);

CREATE INDEX IF NOT EXISTS idx_crimes_date ON crimes(date_reported);
CREATE INDEX IF NOT EXISTS idx_crimes_zone ON crimes(zone);
CREATE INDEX IF NOT EXISTS idx_crimes_status ON crimes(status);
"""


def init_db():
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def table_has_rows():
    with db_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS c FROM crimes")
        return cur.fetchone()["c"] > 0
