"""003 — Create learning pattern tracking tables.

Three new tables for error metadata extraction, aggregation, and session linking.
All additive — no existing tables modified.

Tables:
  - learning_pattern: raw per-attempt error metadata
  - error_pattern: aggregated error counts per skill + error type
  - session_error: links game sessions to error patterns
"""

from sqlalchemy import text

TABLES = [
    """CREATE TABLE IF NOT EXISTS learningpattern (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_id INTEGER NOT NULL REFERENCES skill(id) ON DELETE CASCADE,
        skill_type VARCHAR NOT NULL,
        session_id INTEGER NOT NULL,
        round_id INTEGER NOT NULL,
        attempt_id INTEGER NOT NULL,
        error_type VARCHAR NOT NULL,
        error_detail TEXT,
        level INTEGER NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    "CREATE INDEX IF NOT EXISTS ix_learningpattern_skill_id ON learningpattern(skill_id)",
    "CREATE INDEX IF NOT EXISTS ix_learningpattern_created_at ON learningpattern(created_at)",
    """CREATE TABLE IF NOT EXISTS errorpattern (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_id INTEGER NOT NULL REFERENCES skill(id) ON DELETE CASCADE,
        skill_type VARCHAR NOT NULL,
        error_type VARCHAR NOT NULL,
        count INTEGER NOT NULL DEFAULT 0,
        severity FLOAT NOT NULL DEFAULT 0.0,
        last_seen DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(skill_id, error_type)
    )""",
    """CREATE TABLE IF NOT EXISTS sessionerror (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        session_type VARCHAR NOT NULL,
        error_pattern_id INTEGER NOT NULL REFERENCES errorpattern(id) ON DELETE CASCADE,
        confidence FLOAT NOT NULL DEFAULT 1.0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
]


def up(conn):
    """Create the three learning pattern tables."""
    for stmt in TABLES:
        conn.execute(text(stmt))


MIGRATION = {
    "version": 3,
    "name": "learning_patterns",
    "up": up,
}
